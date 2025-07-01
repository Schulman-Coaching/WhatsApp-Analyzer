#!/usr/bin/env python3
"""
Proper STDIO MCP Client

This module provides a correct implementation of the MCP protocol over STDIO,
handling the proper initialization handshake and message exchange.
"""

import asyncio
import json
import uuid
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MCPCapabilities:
    """MCP client capabilities"""
    roots: Optional[Dict[str, Any]] = None
    sampling: Optional[Dict[str, Any]] = None


class MCPStdioClient:
    """Proper MCP STDIO client with correct protocol implementation"""
    
    def __init__(self, server_executable: str):
        self.server_executable = server_executable
        self.process: Optional[asyncio.subprocess.Process] = None
        self.initialized = False
        self.server_info: Optional[Dict[str, Any]] = None
        self.request_id = 0
        
    async def start(self) -> bool:
        """Start the MCP server process"""
        try:
            logger.info(f"Starting MCP server: {self.server_executable}")
            
            self.process = await asyncio.create_subprocess_exec(
                "python", self.server_executable,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            logger.info("MCP server process started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            return False
    
    async def initialize(self) -> bool:
        """Perform MCP initialization handshake"""
        try:
            logger.info("Initializing MCP connection...")
            
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {
                            "listChanged": True
                        },
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "WhatsApp-Analyzer",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send request
            await self._send_request(init_request)
            
            # Wait for response
            response = await self._read_response()
            
            if response and response.get("id") == init_request["id"]:
                if "error" in response:
                    logger.error(f"Initialization error: {response['error']}")
                    return False
                
                self.server_info = response.get("result", {})
                logger.info(f"Server info: {self.server_info}")
                
                # Send initialized notification
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                
                await self._send_request(initialized_notification)
                
                self.initialized = True
                logger.info("MCP initialization completed successfully")
                return True
            else:
                logger.error("Invalid initialization response")
                return False
                
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        if not self.initialized:
            raise RuntimeError("MCP client not initialized")
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            logger.info(f"Calling tool: {tool_name} with args: {arguments}")
            
            # Send request
            await self._send_request(request)
            
            # Wait for response
            response = await self._read_response()
            
            if response and response.get("id") == request["id"]:
                if "error" in response:
                    raise Exception(f"Tool call error: {response['error']}")
                
                result = response.get("result", {})
                logger.info(f"Tool call successful, result type: {type(result)}")
                return result
            else:
                raise Exception("Invalid tool call response")
                
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        if not self.initialized:
            raise RuntimeError("MCP client not initialized")
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/list"
            }
            
            await self._send_request(request)
            response = await self._read_response()
            
            if response and response.get("id") == request["id"]:
                if "error" in response:
                    raise Exception(f"List tools error: {response['error']}")
                
                tools = response.get("result", {}).get("tools", [])
                logger.info(f"Found {len(tools)} tools")
                return tools
            else:
                raise Exception("Invalid list tools response")
                
        except Exception as e:
            logger.error(f"List tools failed: {e}")
            raise
    
    async def close(self):
        """Close the MCP connection"""
        try:
            if self.process:
                self.process.terminate()
                await self.process.wait()
                logger.info("MCP server process terminated")
        except Exception as e:
            logger.error(f"Error closing MCP connection: {e}")
    
    def _next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def _send_request(self, request: Dict[str, Any]):
        """Send a request to the MCP server"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("MCP server process not available")
        
        request_str = json.dumps(request) + "\n"
        logger.debug(f"Sending: {request_str.strip()}")
        
        self.process.stdin.write(request_str.encode())
        await self.process.stdin.drain()
    
    async def _read_response(self, timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """Read a response from the MCP server"""
        if not self.process or not self.process.stdout:
            raise RuntimeError("MCP server process not available")
        
        try:
            # Read line with timeout
            line_bytes = await asyncio.wait_for(
                self.process.stdout.readline(),
                timeout=timeout
            )
            
            if not line_bytes:
                logger.warning("No response received")
                return None
            
            line = line_bytes.decode().strip()
            logger.debug(f"Received: {line}")
            
            if line:
                return json.loads(line)
            else:
                return None
                
        except asyncio.TimeoutError:
            logger.error(f"Response timeout after {timeout} seconds")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading response: {e}")
            return None


async def test_mcp_connection():
    """Test the MCP connection with proper protocol"""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    server_path = r"C:\Users\elie\OneDrive\Documents\Cline\MCP\whatsapp-mcp\whatsapp-mcp-server\main.py"
    
    client = MCPStdioClient(server_path)
    
    try:
        print("🚀 Testing MCP connection...")
        
        # Start server
        if not await client.start():
            print("❌ Failed to start server")
            return False
        
        # Wait a moment for server to start
        await asyncio.sleep(1)
        
        # Initialize
        if not await client.initialize():
            print("❌ Failed to initialize")
            return False
        
        print("✅ MCP connection initialized successfully")
        
        # List tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        
        # Test a simple tool call
        print("\n🧪 Testing list_chats tool...")
        try:
            result = await client.call_tool("list_chats", {
                "limit": 3,
                "page": 0,
                "include_last_message": True,
                "sort_by": "last_active"
            })
            
            print("✅ list_chats call successful!")
            print(f"Result type: {type(result)}")
            
            if isinstance(result, list):
                print(f"Found {len(result)} chats")
                for i, chat in enumerate(result[:3]):
                    name = chat.get("name", "Unknown")
                    jid = chat.get("jid", "Unknown")
                    print(f"  {i+1}. {name} ({jid})")
            elif isinstance(result, dict):
                print(f"Result keys: {list(result.keys())}")
            
            return True
            
        except Exception as e:
            print(f"❌ Tool call failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_mcp_connection())