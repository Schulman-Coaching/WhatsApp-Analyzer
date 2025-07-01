#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Client Implementation

This module provides a robust MCP client infrastructure for connecting to
MCP servers and executing tools with proper error handling, retry logic,
and session management.
"""

import json
import asyncio
import logging
import time
import uuid
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import websockets
from urllib.parse import urlparse


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPConnectionType(Enum):
    """MCP connection types"""
    STDIO = "stdio"
    SSE = "sse"
    WEBSOCKET = "websocket"


class MCPClientError(Exception):
    """Base exception for MCP client errors"""
    pass


class MCPConnectionError(MCPClientError):
    """Exception raised when connection to MCP server fails"""
    pass


class MCPToolError(MCPClientError):
    """Exception raised when MCP tool execution fails"""
    pass


class MCPAuthenticationError(MCPClientError):
    """Exception raised when MCP authentication fails"""
    pass


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server connection"""
    name: str
    connection_type: MCPConnectionType
    endpoint: str
    auth_token: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    health_check_interval: int = 60
    session_timeout: int = 3600  # 1 hour
    custom_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class MCPSession:
    """Represents an active MCP session"""
    session_id: str
    server_name: str
    created_at: datetime
    last_activity: datetime
    is_active: bool = True
    connection_info: Dict[str, Any] = field(default_factory=dict)


class MCPClient:
    """
    Main MCP client class that handles connections to MCP servers,
    tool execution, and session management.
    """
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.sessions: Dict[str, MCPSession] = {}
        self.connections: Dict[str, Any] = {}
        self._health_check_tasks: Dict[str, asyncio.Task] = {}
        self._session_cleanup_task: Optional[asyncio.Task] = None
        
    def add_server(self, config: MCPServerConfig) -> None:
        """Add a server configuration to the client"""
        self.servers[config.name] = config
        logger.info(f"Added MCP server configuration: {config.name}")
        
    def remove_server(self, server_name: str) -> None:
        """Remove a server configuration and close any active connections"""
        if server_name in self.servers:
            # Close connection if active
            if server_name in self.connections:
                asyncio.create_task(self._close_connection(server_name))
            
            # Remove from servers
            del self.servers[server_name]
            logger.info(f"Removed MCP server: {server_name}")
    
    async def connect(self, server_name: str) -> bool:
        """
        Establish connection to an MCP server
        
        Args:
            server_name: Name of the server to connect to
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if server_name not in self.servers:
            raise MCPConnectionError(f"Server '{server_name}' not configured")
            
        config = self.servers[server_name]
        
        try:
            if config.connection_type == MCPConnectionType.SSE:
                success = await self._connect_sse(server_name, config)
            elif config.connection_type == MCPConnectionType.WEBSOCKET:
                success = await self._connect_websocket(server_name, config)
            elif config.connection_type == MCPConnectionType.STDIO:
                success = await self._connect_stdio(server_name, config)
            else:
                raise MCPConnectionError(f"Unsupported connection type: {config.connection_type}")
                
            if success:
                # Create session
                session = MCPSession(
                    session_id=str(uuid.uuid4()),
                    server_name=server_name,
                    created_at=datetime.now(),
                    last_activity=datetime.now()
                )
                self.sessions[server_name] = session
                
                # Start health check
                self._health_check_tasks[server_name] = asyncio.create_task(
                    self._health_check_loop(server_name)
                )
                
                logger.info(f"Successfully connected to MCP server: {server_name}")
                return True
            else:
                logger.error(f"Failed to connect to MCP server: {server_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to MCP server {server_name}: {e}")
            raise MCPConnectionError(f"Failed to connect to {server_name}: {e}")
    
    async def disconnect(self, server_name: str) -> None:
        """Disconnect from an MCP server"""
        await self._close_connection(server_name)
        
    async def disconnect_all(self) -> None:
        """Disconnect from all MCP servers"""
        tasks = []
        for server_name in list(self.connections.keys()):
            tasks.append(self._close_connection(server_name))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
        # Cancel session cleanup task
        if self._session_cleanup_task:
            self._session_cleanup_task.cancel()
    
    async def execute_tool(
        self, 
        server_name: str, 
        tool_name: str, 
        arguments: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool on an MCP server
        
        Args:
            server_name: Name of the server
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            timeout: Optional timeout override
            
        Returns:
            Dict containing the tool execution result
        """
        if server_name not in self.connections:
            # Try to connect if not already connected
            if not await self.connect(server_name):
                raise MCPConnectionError(f"Cannot connect to server: {server_name}")
        
        config = self.servers[server_name]
        effective_timeout = timeout or config.timeout
        
        # Update session activity
        if server_name in self.sessions:
            self.sessions[server_name].last_activity = datetime.now()
        
        # Retry logic
        last_exception = None
        for attempt in range(config.max_retries):
            try:
                result = await self._execute_tool_request(
                    server_name, tool_name, arguments, effective_timeout
                )
                logger.info(f"Successfully executed tool {tool_name} on {server_name}")
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Tool execution attempt {attempt + 1} failed: {e}")
                
                if attempt < config.max_retries - 1:
                    await asyncio.sleep(config.retry_delay * (2 ** attempt))  # Exponential backoff
                    
                    # Try to reconnect if connection was lost
                    if isinstance(e, MCPConnectionError):
                        logger.info(f"Attempting to reconnect to {server_name}")
                        await self.connect(server_name)
        
        # All retries failed
        raise MCPToolError(f"Tool execution failed after {config.max_retries} attempts: {last_exception}")
    
    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List available tools on an MCP server"""
        try:
            result = await self.execute_tool(server_name, "list_tools", {})
            return result.get("tools", [])
        except Exception as e:
            logger.error(f"Failed to list tools for {server_name}: {e}")
            return []
    
    async def health_check(self, server_name: str) -> bool:
        """Perform health check on an MCP server"""
        try:
            if server_name not in self.connections:
                return False
                
            # Try a simple ping or list_tools call
            await self.execute_tool(server_name, "ping", {})
            return True
            
        except Exception:
            return False
    
    def get_session_info(self, server_name: str) -> Optional[MCPSession]:
        """Get session information for a server"""
        return self.sessions.get(server_name)
    
    def is_connected(self, server_name: str) -> bool:
        """Check if connected to a server"""
        return (server_name in self.connections and 
                server_name in self.sessions and 
                self.sessions[server_name].is_active)
    
    # Private methods for connection handling
    
    async def _connect_sse(self, server_name: str, config: MCPServerConfig) -> bool:
        """Connect to MCP server via Server-Sent Events"""
        try:
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                **config.custom_headers
            }
            
            if config.auth_token:
                headers["Authorization"] = f"Bearer {config.auth_token}"
            
            session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=config.timeout),
                headers=headers
            )
            
            # Test connection
            async with session.get(config.endpoint) as response:
                if response.status != 200:
                    await session.close()
                    raise MCPConnectionError(f"HTTP {response.status}: {response.reason}")
            
            self.connections[server_name] = {
                "type": "sse",
                "session": session,
                "endpoint": config.endpoint
            }
            
            return True
            
        except Exception as e:
            logger.error(f"SSE connection failed for {server_name}: {e}")
            return False
    
    async def _connect_websocket(self, server_name: str, config: MCPServerConfig) -> bool:
        """Connect to MCP server via WebSocket"""
        try:
            headers = config.custom_headers.copy()
            if config.auth_token:
                headers["Authorization"] = f"Bearer {config.auth_token}"
            
            websocket = await websockets.connect(
                config.endpoint,
                extra_headers=headers,
                ping_interval=20,
                ping_timeout=10
            )
            
            self.connections[server_name] = {
                "type": "websocket",
                "websocket": websocket,
                "endpoint": config.endpoint
            }
            
            return True
            
        except Exception as e:
            logger.error(f"WebSocket connection failed for {server_name}: {e}")
            return False
    
    async def _connect_stdio(self, server_name: str, config: MCPServerConfig) -> bool:
        """Connect to MCP server via STDIO"""
        try:
            # For STDIO connections, we would typically start a subprocess
            # This is a simplified implementation
            process = await asyncio.create_subprocess_exec(
                config.endpoint,  # Assuming endpoint is the executable path
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.connections[server_name] = {
                "type": "stdio",
                "process": process,
                "endpoint": config.endpoint
            }
            
            return True
            
        except Exception as e:
            logger.error(f"STDIO connection failed for {server_name}: {e}")
            return False
    
    async def _execute_tool_request(
        self, 
        server_name: str, 
        tool_name: str, 
        arguments: Dict[str, Any],
        timeout: int
    ) -> Dict[str, Any]:
        """Execute the actual tool request based on connection type"""
        connection = self.connections[server_name]
        connection_type = connection["type"]
        
        request_data = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        if connection_type == "sse":
            return await self._execute_sse_request(connection, request_data, timeout)
        elif connection_type == "websocket":
            return await self._execute_websocket_request(connection, request_data, timeout)
        elif connection_type == "stdio":
            return await self._execute_stdio_request(connection, request_data, timeout)
        else:
            raise MCPToolError(f"Unsupported connection type: {connection_type}")
    
    async def _execute_sse_request(
        self, 
        connection: Dict[str, Any], 
        request_data: Dict[str, Any],
        timeout: int
    ) -> Dict[str, Any]:
        """Execute request via SSE"""
        session = connection["session"]
        endpoint = connection["endpoint"]
        
        try:
            async with session.post(
                f"{endpoint}/tools/call",
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status != 200:
                    raise MCPToolError(f"HTTP {response.status}: {response.reason}")
                
                result = await response.json()
                
                if "error" in result:
                    raise MCPToolError(f"Tool error: {result['error']}")
                
                return result.get("result", {})
                
        except asyncio.TimeoutError:
            raise MCPToolError(f"Tool execution timed out after {timeout} seconds")
    
    async def _execute_websocket_request(
        self, 
        connection: Dict[str, Any], 
        request_data: Dict[str, Any],
        timeout: int
    ) -> Dict[str, Any]:
        """Execute request via WebSocket"""
        websocket = connection["websocket"]
        
        try:
            # Send request
            await websocket.send(json.dumps(request_data))
            
            # Wait for response with timeout
            response_str = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            response = json.loads(response_str)
            
            if "error" in response:
                raise MCPToolError(f"Tool error: {response['error']}")
            
            return response.get("result", {})
            
        except asyncio.TimeoutError:
            raise MCPToolError(f"Tool execution timed out after {timeout} seconds")
        except websockets.exceptions.ConnectionClosed:
            raise MCPConnectionError("WebSocket connection closed")
    
    async def _execute_stdio_request(
        self, 
        connection: Dict[str, Any], 
        request_data: Dict[str, Any],
        timeout: int
    ) -> Dict[str, Any]:
        """Execute request via STDIO"""
        process = connection["process"]
        
        try:
            # Send request
            request_str = json.dumps(request_data) + "\n"
            process.stdin.write(request_str.encode())
            await process.stdin.drain()
            
            # Read response with timeout
            response_bytes = await asyncio.wait_for(
                process.stdout.readline(), 
                timeout=timeout
            )
            response_str = response_bytes.decode().strip()
            response = json.loads(response_str)
            
            if "error" in response:
                raise MCPToolError(f"Tool error: {response['error']}")
            
            return response.get("result", {})
            
        except asyncio.TimeoutError:
            raise MCPToolError(f"Tool execution timed out after {timeout} seconds")
    
    async def _close_connection(self, server_name: str) -> None:
        """Close connection to a server"""
        try:
            # Cancel health check task
            if server_name in self._health_check_tasks:
                self._health_check_tasks[server_name].cancel()
                del self._health_check_tasks[server_name]
            
            # Close connection based on type
            if server_name in self.connections:
                connection = self.connections[server_name]
                connection_type = connection["type"]
                
                if connection_type == "sse" and "session" in connection:
                    await connection["session"].close()
                elif connection_type == "websocket" and "websocket" in connection:
                    await connection["websocket"].close()
                elif connection_type == "stdio" and "process" in connection:
                    process = connection["process"]
                    process.terminate()
                    await process.wait()
                
                del self.connections[server_name]
            
            # Mark session as inactive
            if server_name in self.sessions:
                self.sessions[server_name].is_active = False
            
            logger.info(f"Closed connection to MCP server: {server_name}")
            
        except Exception as e:
            logger.error(f"Error closing connection to {server_name}: {e}")
    
    async def _health_check_loop(self, server_name: str) -> None:
        """Background health check loop for a server"""
        config = self.servers[server_name]
        
        while server_name in self.connections:
            try:
                await asyncio.sleep(config.health_check_interval)
                
                if not await self.health_check(server_name):
                    logger.warning(f"Health check failed for {server_name}, attempting reconnect")
                    await self.connect(server_name)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error for {server_name}: {e}")


# Global MCP client instance
_global_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get the global MCP client instance"""
    global _global_client
    if _global_client is None:
        _global_client = MCPClient()
    return _global_client


async def use_mcp_tool(
    server_name: str, 
    tool_name: str, 
    arguments: Dict[str, Any],
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Convenience function to execute an MCP tool using the global client
    
    Args:
        server_name: Name of the MCP server
        tool_name: Name of the tool to execute
        arguments: Tool arguments
        timeout: Optional timeout override
        
    Returns:
        Dict containing the tool execution result
    """
    client = get_mcp_client()
    return await client.execute_tool(server_name, tool_name, arguments, timeout)


# Synchronous wrapper for backward compatibility
def use_mcp_tool_sync(
    server_name: str, 
    tool_name: str, 
    arguments: Dict[str, Any],
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Synchronous wrapper for use_mcp_tool
    
    This function runs the async MCP tool execution in a new event loop
    or the current one if available.
    """
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, we need to use a different approach
            # This is a simplified version - in production you might want to use
            # asyncio.create_task() or run in a thread pool
            import concurrent.futures
            import threading
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(
                        use_mcp_tool(server_name, tool_name, arguments, timeout)
                    )
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result()
        else:
            # Loop exists but not running
            return loop.run_until_complete(
                use_mcp_tool(server_name, tool_name, arguments, timeout)
            )
    except RuntimeError:
        # No event loop exists
        return asyncio.run(
            use_mcp_tool(server_name, tool_name, arguments, timeout)
        )