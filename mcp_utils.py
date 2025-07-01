#!/usr/bin/env python3
"""
MCP Utilities

This module provides utility functions and synchronous wrappers for MCP operations
to maintain backward compatibility with existing synchronous code.
"""

import asyncio
import logging
import functools
from typing import Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor
import threading

from whatsapp_mcp_client import WhatsAppMCPClient, get_whatsapp_mcp_client
from mcp_client import MCPConnectionType
from mcp_config import get_mcp_config, get_whatsapp_settings

logger = logging.getLogger(__name__)

# Thread-local storage for event loops
_thread_local = threading.local()


def get_or_create_event_loop():
    """Get or create an event loop for the current thread"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Event loop is closed")
        return loop
    except RuntimeError:
        # No event loop in current thread, create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def run_async_in_thread(coro):
    """Run an async coroutine in a separate thread with its own event loop"""
    def run_in_new_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_in_new_thread)
        return future.result()


def sync_wrapper(async_func):
    """Decorator to create synchronous wrappers for async functions"""
    @functools.wraps(async_func)
    def wrapper(*args, **kwargs):
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we need to run in a separate thread
                return run_async_in_thread(async_func(*args, **kwargs))
            else:
                # Loop exists but not running
                return loop.run_until_complete(async_func(*args, **kwargs))
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(async_func(*args, **kwargs))
    
    return wrapper


class SyncWhatsAppMCPClient:
    """
    Synchronous wrapper for WhatsAppMCPClient to maintain backward compatibility
    """
    
    def __init__(self, server_name: str = "github.com/lharries/whatsapp-mcp"):
        self.server_name = server_name
        self._async_client: Optional[WhatsAppMCPClient] = None
        self._initialized = False
    
    def _get_client(self) -> WhatsAppMCPClient:
        """Get or create the async client"""
        if self._async_client is None:
            self._async_client = WhatsAppMCPClient(self.server_name)
        return self._async_client
    
    @sync_wrapper
    async def _async_initialize(
        self, 
        endpoint: str,
        connection_type: MCPConnectionType = MCPConnectionType.SSE,
        auth_token: Optional[str] = None
    ) -> bool:
        """Async initialization wrapper"""
        client = self._get_client()
        return await client.initialize(endpoint, connection_type, auth_token)
    
    def initialize(
        self, 
        endpoint: str,
        connection_type: MCPConnectionType = MCPConnectionType.SSE,
        auth_token: Optional[str] = None
    ) -> bool:
        """Initialize the WhatsApp MCP client"""
        result = self._async_initialize(endpoint, connection_type, auth_token)
        self._initialized = result
        return result
    
    @sync_wrapper
    async def _async_authenticate(self, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """Async authentication wrapper"""
        client = self._get_client()
        return await client.authenticate(phone_number)
    
    def authenticate(self, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate with WhatsApp Web"""
        return self._async_authenticate(phone_number)
    
    @sync_wrapper
    async def _async_list_chats(
        self, 
        limit: int = 50, 
        page: int = 0,
        include_last_message: bool = True,
        sort_by: str = "last_active"
    ) -> list:
        """Async list chats wrapper"""
        client = self._get_client()
        return await client.list_chats(limit, page, include_last_message, sort_by)
    
    def list_chats(
        self, 
        limit: int = 50, 
        page: int = 0,
        include_last_message: bool = True,
        sort_by: str = "last_active"
    ) -> list:
        """List WhatsApp chats"""
        return self._async_list_chats(limit, page, include_last_message, sort_by)
    
    @sync_wrapper
    async def _async_get_chat_messages(
        self,
        chat_jid: str,
        limit: int = 100,
        page: int = 0,
        include_context: bool = True,
        context_before: int = 1,
        context_after: int = 1,
        after_date: Optional[str] = None,
        before_date: Optional[str] = None
    ) -> list:
        """Async get chat messages wrapper"""
        client = self._get_client()
        return await client.get_chat_messages(
            chat_jid, limit, page, include_context, 
            context_before, context_after, after_date, before_date
        )
    
    def get_chat_messages(
        self,
        chat_jid: str,
        limit: int = 100,
        page: int = 0,
        include_context: bool = True,
        context_before: int = 1,
        context_after: int = 1,
        after_date: Optional[str] = None,
        before_date: Optional[str] = None
    ) -> list:
        """Get messages from a specific chat"""
        return self._async_get_chat_messages(
            chat_jid, limit, page, include_context,
            context_before, context_after, after_date, before_date
        )
    
    @sync_wrapper
    async def _async_get_connection_status(self) -> Dict[str, Any]:
        """Async get connection status wrapper"""
        client = self._get_client()
        return await client.get_connection_status()
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current WhatsApp connection status"""
        return self._async_get_connection_status()
    
    @sync_wrapper
    async def _async_disconnect(self) -> None:
        """Async disconnect wrapper"""
        if self._async_client:
            await self._async_client.disconnect()
    
    def disconnect(self) -> None:
        """Disconnect from WhatsApp"""
        self._async_disconnect()
        self._initialized = False
    
    def is_initialized(self) -> bool:
        """Check if client is initialized"""
        return self._initialized
    
    def is_authenticated(self) -> bool:
        """Check if authenticated with WhatsApp"""
        if self._async_client:
            return self._async_client.is_authenticated()
        return False
    
    def is_connected(self) -> bool:
        """Check if connected to MCP server"""
        if self._async_client:
            return self._async_client.is_connected()
        return False


# Global sync client instance
_global_sync_client: Optional[SyncWhatsAppMCPClient] = None


def get_sync_whatsapp_client() -> SyncWhatsAppMCPClient:
    """Get the global synchronous WhatsApp MCP client"""
    global _global_sync_client
    if _global_sync_client is None:
        _global_sync_client = SyncWhatsAppMCPClient()
    return _global_sync_client


def use_mcp_tool(
    server_name: str,
    tool_name: str,
    arguments: Dict[str, Any],
    timeout: Optional[int] = None
) -> Union[Dict[str, Any], list]:
    """
    Synchronous function to execute MCP tools
    
    This function provides backward compatibility for existing code
    that expects synchronous MCP tool execution.
    
    Args:
        server_name: Name of the MCP server
        tool_name: Name of the tool to execute
        arguments: Tool arguments
        timeout: Optional timeout override
        
    Returns:
        Tool execution result
    """
    try:
        if "whatsapp" in server_name.lower():
            client = get_sync_whatsapp_client()
            
            # Auto-initialize if not already done
            if not client.is_initialized():
                # Try to initialize with default settings
                # In production, these should be configured properly
                default_endpoint = "http://localhost:3000"  # Default MCP server endpoint
                success = client.initialize(default_endpoint)
                if not success:
                    raise RuntimeError("Failed to initialize WhatsApp MCP client")
            
            # Map tool names to client methods
            if tool_name == "list_chats":
                return client.list_chats(**arguments)
            elif tool_name == "list_messages":
                chat_jid = arguments.pop("chat_jid")
                return client.get_chat_messages(chat_jid, **arguments)
            elif tool_name == "authenticate":
                return client.authenticate(arguments.get("phone_number"))
            elif tool_name == "get_status":
                return client.get_connection_status()
            else:
                # For unknown tools, try to use the generic async approach
                @sync_wrapper
                async def execute_generic_tool():
                    from whatsapp_mcp_client import use_mcp_tool as async_use_mcp_tool
                    return await async_use_mcp_tool(server_name, tool_name, arguments, timeout)
                
                return execute_generic_tool()
        else:
            # For non-WhatsApp servers, use generic MCP client
            @sync_wrapper
            async def execute_generic_tool():
                from mcp_client import use_mcp_tool as async_use_mcp_tool
                return await async_use_mcp_tool(server_name, tool_name, arguments, timeout)
            
            return execute_generic_tool()
            
    except Exception as e:
        logger.error(f"MCP tool execution failed: {e}")
        raise


def initialize_whatsapp_mcp(
    endpoint: Optional[str] = None,
    connection_type: Optional[str] = None,
    auth_token: Optional[str] = None,
    use_config: bool = True
) -> bool:
    """
    Initialize the WhatsApp MCP client with configuration
    
    Args:
        endpoint: MCP server endpoint (overrides config)
        connection_type: Connection type (overrides config)
        auth_token: Optional authentication token (overrides config)
        use_config: Whether to use configuration file settings
        
    Returns:
        bool: True if initialization successful
    """
    try:
        client = get_sync_whatsapp_client()
        
        # Get settings from config if requested
        if use_config:
            settings = get_whatsapp_settings()
            endpoint = endpoint or settings.server.endpoint
            connection_type = connection_type or settings.server.connection_type
            auth_token = auth_token or settings.server.auth_token
        else:
            # Use defaults if no config
            endpoint = endpoint or "http://localhost:3000"
            connection_type = connection_type or "sse"
        
        # Convert string to enum
        conn_type = MCPConnectionType.SSE
        if connection_type.lower() == "websocket":
            conn_type = MCPConnectionType.WEBSOCKET
        elif connection_type.lower() == "stdio":
            conn_type = MCPConnectionType.STDIO
        
        return client.initialize(endpoint, conn_type, auth_token)
        
    except Exception as e:
        logger.error(f"WhatsApp MCP initialization failed: {e}")
        return False


def cleanup_mcp_connections():
    """Clean up all MCP connections"""
    try:
        global _global_sync_client
        if _global_sync_client:
            _global_sync_client.disconnect()
            _global_sync_client = None
        
        # Also cleanup async clients
        from whatsapp_mcp_client import _global_whatsapp_client
        if _global_whatsapp_client:
            @sync_wrapper
            async def cleanup_async():
                await _global_whatsapp_client.disconnect()
            
            cleanup_async()
        
        logger.info("MCP connections cleaned up")
        
    except Exception as e:
        logger.error(f"Error during MCP cleanup: {e}")