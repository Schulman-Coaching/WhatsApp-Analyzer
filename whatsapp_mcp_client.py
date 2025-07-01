#!/usr/bin/env python3
"""
WhatsApp-specific MCP Client

This module provides a specialized MCP client for WhatsApp data extraction
with WhatsApp-specific functionality, rate limiting, and session management.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from mcp_client import (
    MCPClient, MCPServerConfig, MCPConnectionType, 
    MCPClientError, MCPConnectionError, MCPToolError
)

logger = logging.getLogger(__name__)


@dataclass
class WhatsAppRateLimits:
    """Rate limiting configuration for WhatsApp operations"""
    messages_per_minute: int = 60
    chats_per_minute: int = 30
    requests_per_second: int = 2
    burst_limit: int = 10
    cooldown_period: int = 300  # 5 minutes


@dataclass
class WhatsAppSession:
    """WhatsApp session state information"""
    is_authenticated: bool = False
    phone_number: Optional[str] = None
    session_start: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    qr_code_required: bool = False
    connection_status: str = "disconnected"
    rate_limit_resets: Dict[str, datetime] = None
    
    def __post_init__(self):
        if self.rate_limit_resets is None:
            self.rate_limit_resets = {}


class WhatsAppMCPClient:
    """
    Specialized MCP client for WhatsApp data extraction with enhanced
    functionality for WhatsApp Web integration, rate limiting, and
    session persistence.
    """
    
    def __init__(self, server_name: str = "github.com/lharries/whatsapp-mcp"):
        self.server_name = server_name
        self.mcp_client = MCPClient()
        self.rate_limits = WhatsAppRateLimits()
        self.session = WhatsAppSession()
        self._request_timestamps: List[float] = []
        self._rate_limit_lock = asyncio.Lock()
        
    async def initialize(
        self, 
        endpoint: str,
        connection_type: MCPConnectionType = MCPConnectionType.SSE,
        auth_token: Optional[str] = None,
        custom_rate_limits: Optional[WhatsAppRateLimits] = None
    ) -> bool:
        """
        Initialize the WhatsApp MCP client with server configuration
        
        Args:
            endpoint: MCP server endpoint URL
            connection_type: Type of connection (SSE, WebSocket, STDIO)
            auth_token: Optional authentication token
            custom_rate_limits: Custom rate limiting configuration
            
        Returns:
            bool: True if initialization successful
        """
        try:
            # Apply custom rate limits if provided
            if custom_rate_limits:
                self.rate_limits = custom_rate_limits
            
            # Configure MCP server
            config = MCPServerConfig(
                name=self.server_name,
                connection_type=connection_type,
                endpoint=endpoint,
                auth_token=auth_token,
                timeout=60,  # Longer timeout for WhatsApp operations
                max_retries=5,  # More retries for reliability
                retry_delay=2.0,
                health_check_interval=30,
                session_timeout=7200,  # 2 hours
                custom_headers={
                    "User-Agent": "WhatsApp-MCP-Client/1.0",
                    "Accept": "application/json"
                }
            )
            
            self.mcp_client.add_server(config)
            
            # Establish connection
            success = await self.mcp_client.connect(self.server_name)
            if success:
                logger.info("WhatsApp MCP client initialized successfully")
                return True
            else:
                logger.error("Failed to initialize WhatsApp MCP client")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing WhatsApp MCP client: {e}")
            return False
    
    async def authenticate(self, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Authenticate with WhatsApp Web
        
        Args:
            phone_number: Optional phone number for authentication
            
        Returns:
            Dict containing authentication status and QR code if needed
        """
        try:
            await self._enforce_rate_limit("auth")
            
            auth_args = {}
            if phone_number:
                auth_args["phone_number"] = phone_number
            
            result = await self.mcp_client.execute_tool(
                self.server_name,
                "authenticate",
                auth_args,
                timeout=120  # Authentication can take longer
            )
            
            # Update session state
            self.session.phone_number = phone_number
            self.session.session_start = datetime.now()
            self.session.last_activity = datetime.now()
            
            if result.get("status") == "authenticated":
                self.session.is_authenticated = True
                self.session.connection_status = "connected"
                self.session.qr_code_required = False
                logger.info("WhatsApp authentication successful")
            elif result.get("qr_code"):
                self.session.qr_code_required = True
                self.session.connection_status = "awaiting_qr"
                logger.info("QR code required for WhatsApp authentication")
            
            return result
            
        except Exception as e:
            logger.error(f"WhatsApp authentication failed: {e}")
            self.session.connection_status = "error"
            raise MCPClientError(f"Authentication failed: {e}")
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Get current WhatsApp connection status"""
        try:
            await self._enforce_rate_limit("status")
            
            result = await self.mcp_client.execute_tool(
                self.server_name,
                "get_status",
                {}
            )
            
            # Update session state
            if result.get("is_connected"):
                self.session.connection_status = "connected"
                self.session.is_authenticated = True
            else:
                self.session.connection_status = "disconnected"
                self.session.is_authenticated = False
            
            self.session.last_activity = datetime.now()
            return result
            
        except Exception as e:
            logger.error(f"Failed to get connection status: {e}")
            self.session.connection_status = "error"
            return {"is_connected": False, "error": str(e)}
    
    async def list_chats(
        self, 
        limit: int = 50, 
        page: int = 0,
        include_last_message: bool = True,
        sort_by: str = "last_active"
    ) -> List[Dict[str, Any]]:
        """
        List WhatsApp chats with pagination
        
        Args:
            limit: Maximum number of chats to return
            page: Page number for pagination
            include_last_message: Whether to include last message info
            sort_by: Sort criteria (last_active, name, etc.)
            
        Returns:
            List of chat dictionaries
        """
        try:
            await self._enforce_rate_limit("chats")
            
            result = await self.mcp_client.execute_tool(
                self.server_name,
                "list_chats",
                {
                    "limit": limit,
                    "page": page,
                    "include_last_message": include_last_message,
                    "sort_by": sort_by
                }
            )
            
            self.session.last_activity = datetime.now()
            
            # Ensure we return a list
            if isinstance(result, dict) and "chats" in result:
                return result["chats"]
            elif isinstance(result, list):
                return result
            else:
                logger.warning(f"Unexpected chat list format: {type(result)}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to list chats: {e}")
            raise MCPToolError(f"Chat listing failed: {e}")
    
    async def get_chat_messages(
        self,
        chat_jid: str,
        limit: int = 100,
        page: int = 0,
        include_context: bool = True,
        context_before: int = 1,
        context_after: int = 1,
        after_date: Optional[str] = None,
        before_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a specific chat
        
        Args:
            chat_jid: Chat identifier
            limit: Maximum number of messages to return
            page: Page number for pagination
            include_context: Whether to include context messages
            context_before: Number of context messages before
            context_after: Number of context messages after
            after_date: ISO date string to filter messages after
            before_date: ISO date string to filter messages before
            
        Returns:
            List of message dictionaries
        """
        try:
            await self._enforce_rate_limit("messages")
            
            args = {
                "chat_jid": chat_jid,
                "limit": limit,
                "page": page,
                "include_context": include_context,
                "context_before": context_before,
                "context_after": context_after
            }
            
            if after_date:
                args["after"] = after_date
            if before_date:
                args["before"] = before_date
            
            result = await self.mcp_client.execute_tool(
                self.server_name,
                "list_messages",
                args
            )
            
            self.session.last_activity = datetime.now()
            
            # Ensure we return a list
            if isinstance(result, dict) and "messages" in result:
                return result["messages"]
            elif isinstance(result, list):
                return result
            else:
                logger.warning(f"Unexpected message list format: {type(result)}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get messages for chat {chat_jid}: {e}")
            raise MCPToolError(f"Message retrieval failed: {e}")
    
    async def search_messages(
        self,
        query: str,
        chat_jid: Optional[str] = None,
        limit: int = 50,
        message_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for messages across chats
        
        Args:
            query: Search query string
            chat_jid: Optional specific chat to search in
            limit: Maximum number of results
            message_types: Optional list of message types to include
            
        Returns:
            List of matching message dictionaries
        """
        try:
            await self._enforce_rate_limit("search")
            
            args = {
                "query": query,
                "limit": limit
            }
            
            if chat_jid:
                args["chat_jid"] = chat_jid
            if message_types:
                args["message_types"] = message_types
            
            result = await self.mcp_client.execute_tool(
                self.server_name,
                "search_messages",
                args
            )
            
            self.session.last_activity = datetime.now()
            
            # Ensure we return a list
            if isinstance(result, dict) and "messages" in result:
                return result["messages"]
            elif isinstance(result, list):
                return result
            else:
                return []
                
        except Exception as e:
            logger.error(f"Message search failed: {e}")
            raise MCPToolError(f"Message search failed: {e}")
    
    async def get_chat_info(self, chat_jid: str) -> Dict[str, Any]:
        """Get detailed information about a specific chat"""
        try:
            await self._enforce_rate_limit("info")
            
            result = await self.mcp_client.execute_tool(
                self.server_name,
                "get_chat_info",
                {"chat_jid": chat_jid}
            )
            
            self.session.last_activity = datetime.now()
            return result
            
        except Exception as e:
            logger.error(f"Failed to get chat info for {chat_jid}: {e}")
            raise MCPToolError(f"Chat info retrieval failed: {e}")
    
    async def export_chat(
        self,
        chat_jid: str,
        format: str = "json",
        include_media: bool = False,
        date_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Export a complete chat
        
        Args:
            chat_jid: Chat identifier
            format: Export format (json, csv, txt)
            include_media: Whether to include media files
            date_range: Optional date range filter
            
        Returns:
            Export result with file path or data
        """
        try:
            await self._enforce_rate_limit("export")
            
            args = {
                "chat_jid": chat_jid,
                "format": format,
                "include_media": include_media
            }
            
            if date_range:
                args["date_range"] = date_range
            
            result = await self.mcp_client.execute_tool(
                self.server_name,
                "export_chat",
                args,
                timeout=300  # Exports can take longer
            )
            
            self.session.last_activity = datetime.now()
            return result
            
        except Exception as e:
            logger.error(f"Chat export failed for {chat_jid}: {e}")
            raise MCPToolError(f"Chat export failed: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from WhatsApp and clean up resources"""
        try:
            if self.session.is_authenticated:
                await self.mcp_client.execute_tool(
                    self.server_name,
                    "disconnect",
                    {}
                )
            
            await self.mcp_client.disconnect(self.server_name)
            
            # Reset session state
            self.session.is_authenticated = False
            self.session.connection_status = "disconnected"
            self.session.last_activity = datetime.now()
            
            logger.info("WhatsApp MCP client disconnected")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    def get_session_info(self) -> WhatsAppSession:
        """Get current session information"""
        return self.session
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with WhatsApp"""
        return self.session.is_authenticated
    
    def is_connected(self) -> bool:
        """Check if connected to MCP server"""
        return self.mcp_client.is_connected(self.server_name)
    
    async def _enforce_rate_limit(self, operation_type: str) -> None:
        """
        Enforce rate limiting for different operation types
        
        Args:
            operation_type: Type of operation (chats, messages, auth, etc.)
        """
        async with self._rate_limit_lock:
            now = time.time()
            
            # Clean old timestamps (older than 1 minute)
            self._request_timestamps = [
                ts for ts in self._request_timestamps 
                if now - ts < 60
            ]
            
            # Check rate limits based on operation type
            if operation_type == "messages":
                max_per_minute = self.rate_limits.messages_per_minute
            elif operation_type == "chats":
                max_per_minute = self.rate_limits.chats_per_minute
            else:
                max_per_minute = 30  # Default limit
            
            # Check if we're hitting the per-minute limit
            if len(self._request_timestamps) >= max_per_minute:
                sleep_time = 60 - (now - self._request_timestamps[0])
                if sleep_time > 0:
                    logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                    await asyncio.sleep(sleep_time)
            
            # Check requests per second limit
            recent_requests = [
                ts for ts in self._request_timestamps 
                if now - ts < 1
            ]
            
            if len(recent_requests) >= self.rate_limits.requests_per_second:
                sleep_time = 1 - (now - recent_requests[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            # Add current timestamp
            self._request_timestamps.append(now)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            # Check MCP connection
            mcp_healthy = await self.mcp_client.health_check(self.server_name)
            
            # Check WhatsApp connection if authenticated
            whatsapp_status = None
            if self.session.is_authenticated:
                whatsapp_status = await self.get_connection_status()
            
            return {
                "mcp_connection": mcp_healthy,
                "whatsapp_connection": whatsapp_status,
                "session_info": {
                    "authenticated": self.session.is_authenticated,
                    "connection_status": self.session.connection_status,
                    "last_activity": self.session.last_activity.isoformat() if self.session.last_activity else None,
                    "session_duration": (
                        (datetime.now() - self.session.session_start).total_seconds()
                        if self.session.session_start else None
                    )
                },
                "rate_limits": {
                    "recent_requests": len(self._request_timestamps),
                    "requests_per_minute_limit": self.rate_limits.messages_per_minute
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "mcp_connection": False,
                "whatsapp_connection": None,
                "error": str(e)
            }


# Global WhatsApp MCP client instance
_global_whatsapp_client: Optional[WhatsAppMCPClient] = None


def get_whatsapp_mcp_client() -> WhatsAppMCPClient:
    """Get the global WhatsApp MCP client instance"""
    global _global_whatsapp_client
    if _global_whatsapp_client is None:
        _global_whatsapp_client = WhatsAppMCPClient()
    return _global_whatsapp_client


# Convenience functions for backward compatibility
async def use_mcp_tool(
    server_name: str,
    tool_name: str,
    arguments: Dict[str, Any],
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Convenience function that uses WhatsApp MCP client if server is WhatsApp-related,
    otherwise falls back to generic MCP client
    """
    if "whatsapp" in server_name.lower():
        client = get_whatsapp_mcp_client()
        
        # Map tool names to WhatsApp client methods
        if tool_name == "list_chats":
            result = await client.list_chats(**arguments)
            return result
        elif tool_name == "list_messages":
            chat_jid = arguments.pop("chat_jid")
            result = await client.get_chat_messages(chat_jid, **arguments)
            return result
        elif tool_name == "authenticate":
            result = await client.authenticate(arguments.get("phone_number"))
            return result
        elif tool_name == "get_status":
            result = await client.get_connection_status()
            return result
        else:
            # Fall back to generic MCP client for unknown tools
            from mcp_client import get_mcp_client
            generic_client = get_mcp_client()
            return await generic_client.execute_tool(server_name, tool_name, arguments, timeout)
    else:
        # Use generic MCP client for non-WhatsApp servers
        from mcp_client import get_mcp_client
        generic_client = get_mcp_client()
        return await generic_client.execute_tool(server_name, tool_name, arguments, timeout)