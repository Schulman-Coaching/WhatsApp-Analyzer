# WhatsApp MCP Client Infrastructure Documentation

## Overview

This document describes the MCP (Model Context Protocol) client infrastructure implemented for WhatsApp data extraction. The infrastructure provides a robust, production-ready foundation for connecting to WhatsApp MCP servers and extracting chat data for business intelligence analysis.

## Architecture

The MCP client infrastructure consists of several key components:

### Core Components

1. **`mcp_client.py`** - Base MCP client with protocol implementation
2. **`whatsapp_mcp_client.py`** - WhatsApp-specific MCP client with specialized functionality
3. **`mcp_utils.py`** - Synchronous wrappers and utility functions
4. **`mcp_config.py`** - Configuration management system

### Key Features

- **Multiple Connection Types**: Support for SSE, WebSocket, and STDIO connections
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Session Management**: Persistent session handling with automatic reconnection
- **Error Handling**: Comprehensive error handling with retry logic
- **Health Monitoring**: Automatic health checks and connection monitoring
- **Configuration Management**: Flexible configuration via files or environment variables
- **Backward Compatibility**: Synchronous wrappers for existing code

## Installation

### Dependencies

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Required Packages

- `aiohttp>=3.8.0` - For HTTP/SSE connections
- `websockets>=11.0.0` - For WebSocket connections
- `asyncio` - For asynchronous operations
- `python-dateutil>=2.8.0` - For date/time handling

## Configuration

### Configuration File

Create a `mcp_config.json` file in your project root:

```json
{
  "whatsapp": {
    "server": {
      "name": "github.com/lharries/whatsapp-mcp",
      "endpoint": "http://localhost:3000",
      "connection_type": "sse",
      "auth_token": null,
      "timeout": 60,
      "max_retries": 5,
      "retry_delay": 2.0,
      "health_check_interval": 30,
      "session_timeout": 7200,
      "custom_headers": {
        "User-Agent": "WhatsApp-MCP-Client/1.0",
        "Accept": "application/json"
      }
    },
    "rate_limits": {
      "messages_per_minute": 60,
      "chats_per_minute": 30,
      "requests_per_second": 2,
      "burst_limit": 10,
      "cooldown_period": 300
    },
    "auto_authenticate": false,
    "phone_number": null,
    "session_persistence": true,
    "export_format": "json",
    "include_media": false
  }
}
```

### Environment Variables

You can also configure using environment variables:

```bash
export MCP_WHATSAPP_ENDPOINT="http://localhost:3000"
export MCP_WHATSAPP_CONNECTION_TYPE="sse"
export MCP_WHATSAPP_AUTH_TOKEN="your-token-here"
export MCP_WHATSAPP_PHONE_NUMBER="+1234567890"
export MCP_WHATSAPP_AUTO_AUTH="true"
```

### Generate Sample Configuration

```bash
python mcp_config.py
```

This creates a `mcp_config_sample.json` file you can customize.

## Usage

### Basic Usage (Synchronous)

For backward compatibility with existing code:

```python
from mcp_utils import use_mcp_tool, initialize_whatsapp_mcp

# Initialize the client
success = initialize_whatsapp_mcp()
if not success:
    print("Failed to initialize MCP client")
    exit(1)

# List chats
chats = use_mcp_tool(
    server_name="github.com/lharries/whatsapp-mcp",
    tool_name="list_chats",
    arguments={
        "limit": 50,
        "page": 0,
        "include_last_message": True,
        "sort_by": "last_active"
    }
)

# Get messages from a chat
messages = use_mcp_tool(
    server_name="github.com/lharries/whatsapp-mcp",
    tool_name="list_messages",
    arguments={
        "chat_jid": "1234567890@c.us",
        "limit": 100,
        "page": 0,
        "include_context": True
    }
)
```

### Advanced Usage (Asynchronous)

For new code that can use async/await:

```python
import asyncio
from whatsapp_mcp_client import WhatsAppMCPClient
from mcp_client import MCPConnectionType

async def main():
    # Create client
    client = WhatsAppMCPClient()
    
    # Initialize with custom settings
    await client.initialize(
        endpoint="http://localhost:3000",
        connection_type=MCPConnectionType.SSE,
        auth_token="your-token"
    )
    
    # Authenticate with WhatsApp
    auth_result = await client.authenticate("+1234567890")
    if auth_result.get("qr_code"):
        print("Scan QR code:", auth_result["qr_code"])
    
    # List chats
    chats = await client.list_chats(limit=50, page=0)
    
    # Get messages
    for chat in chats:
        messages = await client.get_chat_messages(
            chat_jid=chat["jid"],
            limit=100
        )
        print(f"Chat {chat['name']}: {len(messages)} messages")
    
    # Cleanup
    await client.disconnect()

# Run the async function
asyncio.run(main())
```

### Using with Existing Extractor

The existing `whatsapp_mcp_extractor.py` has been updated to use the new infrastructure:

```bash
# Basic usage
python whatsapp_mcp_extractor.py

# With custom MCP server
python whatsapp_mcp_extractor.py --mcp-endpoint http://localhost:3000

# With WebSocket connection
python whatsapp_mcp_extractor.py --mcp-connection websocket

# With authentication token
python whatsapp_mcp_extractor.py --auth-token your-token-here

# Limit processing
python whatsapp_mcp_extractor.py --max-chats 10 --max-history 24
```

## API Reference

### MCPClient Class

Base MCP client for generic MCP server connections.

#### Methods

- `add_server(config: MCPServerConfig)` - Add server configuration
- `connect(server_name: str) -> bool` - Connect to server
- `execute_tool(server_name, tool_name, arguments) -> Dict` - Execute tool
- `disconnect(server_name: str)` - Disconnect from server
- `health_check(server_name: str) -> bool` - Check server health

### WhatsAppMCPClient Class

Specialized client for WhatsApp MCP servers.

#### Methods

- `initialize(endpoint, connection_type, auth_token) -> bool` - Initialize client
- `authenticate(phone_number) -> Dict` - Authenticate with WhatsApp
- `list_chats(limit, page, include_last_message, sort_by) -> List` - List chats
- `get_chat_messages(chat_jid, limit, page, ...) -> List` - Get messages
- `search_messages(query, chat_jid, limit) -> List` - Search messages
- `export_chat(chat_jid, format, include_media) -> Dict` - Export chat
- `get_connection_status() -> Dict` - Get connection status
- `disconnect()` - Disconnect and cleanup

### Utility Functions

#### `use_mcp_tool(server_name, tool_name, arguments, timeout=None)`

Synchronous function to execute MCP tools. Automatically handles WhatsApp-specific routing.

#### `initialize_whatsapp_mcp(endpoint=None, connection_type=None, auth_token=None, use_config=True)`

Initialize WhatsApp MCP client with optional parameter overrides.

#### `cleanup_mcp_connections()`

Clean up all MCP connections and resources.

## Error Handling

The infrastructure provides comprehensive error handling:

### Exception Types

- `MCPClientError` - Base exception for MCP client errors
- `MCPConnectionError` - Connection-related errors
- `MCPToolError` - Tool execution errors
- `MCPAuthenticationError` - Authentication failures

### Retry Logic

- Automatic retries with exponential backoff
- Configurable retry count and delay
- Connection recovery on transient failures

### Rate Limiting

- Per-minute limits for different operation types
- Requests-per-second throttling
- Burst protection with cooldown periods

## Monitoring and Health Checks

### Health Check Features

- Automatic periodic health checks
- Connection status monitoring
- Session timeout handling
- Reconnection on failure

### Getting Health Status

```python
from whatsapp_mcp_client import get_whatsapp_mcp_client

client = get_whatsapp_mcp_client()
health = await client.health_check()
print(f"MCP Connection: {health['mcp_connection']}")
print(f"WhatsApp Status: {health['whatsapp_connection']}")
```

## Integration with Existing Code

The new infrastructure is designed to be backward compatible:

### Existing Code Compatibility

1. **No Changes Required**: Existing calls to `use_mcp_tool()` continue to work
2. **Automatic Initialization**: Client auto-initializes with default settings
3. **Configuration Override**: Can override settings via parameters or config files

### Migration Path

1. **Phase 1**: Use existing synchronous interface with new backend
2. **Phase 2**: Gradually migrate to async interface for better performance
3. **Phase 3**: Add advanced features like custom rate limiting and monitoring

## Production Deployment

### Recommended Settings

```json
{
  "whatsapp": {
    "server": {
      "endpoint": "https://your-mcp-server.com",
      "connection_type": "sse",
      "timeout": 120,
      "max_retries": 10,
      "retry_delay": 5.0,
      "health_check_interval": 60
    },
    "rate_limits": {
      "messages_per_minute": 30,
      "chats_per_minute": 15,
      "requests_per_second": 1
    }
  }
}
```

### Security Considerations

1. **Authentication Tokens**: Store securely, use environment variables
2. **Rate Limiting**: Configure conservative limits to avoid blocking
3. **Connection Security**: Use HTTPS/WSS for production endpoints
4. **Session Management**: Enable session persistence for reliability

### Monitoring

1. **Health Checks**: Monitor connection health regularly
2. **Rate Limit Tracking**: Monitor rate limit usage
3. **Error Logging**: Implement comprehensive error logging
4. **Performance Metrics**: Track response times and success rates

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Check MCP server is running
   - Verify endpoint URL and port
   - Check firewall/network settings

2. **Authentication Issues**
   - Verify phone number format
   - Check QR code scanning process
   - Ensure WhatsApp Web is accessible

3. **Rate Limiting**
   - Reduce request frequency
   - Implement proper delays between requests
   - Monitor rate limit status

4. **Tool Execution Failures**
   - Check tool name spelling
   - Verify argument format
   - Review server logs for errors

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Support

1. Check server logs for detailed error messages
2. Enable debug logging for client-side diagnostics
3. Verify MCP server compatibility and version
4. Review configuration settings

## Future Enhancements

Planned improvements include:

1. **Connection Pooling**: Multiple concurrent connections
2. **Advanced Caching**: Response caching for better performance
3. **Metrics Collection**: Built-in performance metrics
4. **Plugin System**: Extensible tool and handler system
5. **Load Balancing**: Multiple server support with failover