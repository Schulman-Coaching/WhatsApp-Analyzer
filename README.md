# WhatsApp Chat Data Analysis for Monetization Opportunities

This project provides a robust, production-ready infrastructure for extracting and analyzing WhatsApp chat data to identify potential monetization opportunities within your conversations.

## 🚀 New: Production-Ready MCP Client Infrastructure

This project now includes a comprehensive MCP (Model Context Protocol) client infrastructure with:

- **Multiple Connection Types**: SSE, WebSocket, and STDIO support
- **Rate Limiting**: Built-in protection against API abuse
- **Session Management**: Persistent sessions with automatic reconnection
- **Error Handling**: Comprehensive error handling with retry logic
- **Health Monitoring**: Automatic health checks and connection monitoring
- **Configuration Management**: Flexible configuration via files or environment variables
- **Backward Compatibility**: Existing code continues to work without changes

## Features

- Extracts all WhatsApp chats and messages using the WhatsApp MCP server
- Analyzes text content for indicators of monetization opportunities
- Categorizes opportunities into:
  - Product opportunities (e.g., purchase intent, product interest)
  - Service needs (e.g., help wanted, service requests)
  - Marketing insights (e.g., sentiment, preferences)
- Generates structured data ready for LLM analysis
- Preserves conversation context for deeper understanding
- Supports filtering by chat or time period
- Production-ready with comprehensive error handling and monitoring

## Getting Started

### Prerequisites

- Python 3.8 or higher (recommended)
- WhatsApp MCP server running
- WhatsApp Web session active

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the MCP client (optional):
   ```bash
   python mcp_config.py  # Creates sample config
   cp mcp_config_sample.json mcp_config.json
   # Edit mcp_config.json with your settings
   ```

3. Test the MCP client infrastructure:
   ```bash
   python test_mcp_client.py
   ```

4. Ensure the WhatsApp MCP server is running:
   ```bash
   python C:\Users\elie\OneDrive\Documents\Cline\MCP\whatsapp-mcp\whatsapp-mcp-server\main.py
   ```

5. Run the extraction script:
   ```bash
   python extract_whatsapp_data.py
   ```

### Advanced Usage

The new MCP client supports advanced configuration:

```bash
# Use custom MCP server endpoint
python whatsapp_mcp_extractor.py --mcp-endpoint http://localhost:3000

# Use WebSocket connection instead of SSE
python whatsapp_mcp_extractor.py --mcp-connection websocket

# Use authentication token
python whatsapp_mcp_extractor.py --auth-token your-token-here

# Combine with existing options
python whatsapp_mcp_extractor.py --max-chats 10 --mcp-endpoint http://localhost:3000
```

### Usage Options

The extraction script supports several options:

```
python extract_whatsapp_data.py [options]

Options:
  --max-chats MAX_CHATS    Maximum number of chats to process (default: all)
  --max-history MAX_HISTORY Maximum history in hours to extract (default: all)
  --verbose                Display verbose output during extraction
  -h, --help               Show help message and exit
```

Examples:

- Extract all chats:
  ```
  python extract_whatsapp_data.py
  ```

- Extract only the 10 most recent chats:
  ```
  python extract_whatsapp_data.py --max-chats 10
  ```

- Extract messages from the last 24 hours:
  ```
  python extract_whatsapp_data.py --max-history 24
  ```

- Show detailed progress during extraction:
  ```
  python extract_whatsapp_data.py --verbose
  ```
  
  ## MCP Client Architecture
  
  The project includes a comprehensive MCP client infrastructure:
  
  ### Core Components
  
  - **`mcp_client.py`**: Base MCP client with protocol implementation
  - **`whatsapp_mcp_client.py`**: WhatsApp-specific client with specialized functionality
  - **`mcp_utils.py`**: Synchronous wrappers for backward compatibility
  - **`mcp_config.py`**: Configuration management system
  
  ### Key Features
  
  - **Connection Management**: Automatic connection handling with health checks
  - **Rate Limiting**: Configurable rate limits to prevent API abuse
  - **Session Persistence**: Maintains sessions across reconnections
  - **Error Recovery**: Automatic retry logic with exponential backoff
  - **Multiple Protocols**: Support for SSE, WebSocket, and STDIO connections
  
  ## Configuration
  
  ### Configuration File
  
  Create `mcp_config.json` to customize settings:
  
  ```json
  {
    "whatsapp": {
      "server": {
        "endpoint": "http://localhost:3000",
        "connection_type": "sse",
        "timeout": 60,
        "max_retries": 5
      },
      "rate_limits": {
        "messages_per_minute": 60,
        "chats_per_minute": 30,
        "requests_per_second": 2
      }
    }
  }
  ```
  
  ### Environment Variables
  
  ```bash
  export MCP_WHATSAPP_ENDPOINT="http://localhost:3000"
  export MCP_WHATSAPP_CONNECTION_TYPE="sse"
  export MCP_WHATSAPP_AUTH_TOKEN="your-token"
  ```
  
  ## Output Structure

The script creates an `extracted_data` directory with the following files:

- `all_chats.json`: List of all extracted chats
- `whatsapp_data_complete.json`: Complete dataset with all chats and messages
- `llm_analysis_data.json`: Preprocessed data optimized for LLM analysis
- `extraction_metadata.json`: Statistics about the extraction process

For each chat, individual files are also created:
- `chat_[JID].json`: Complete data for the specific chat
- `monetization_[JID].json`: Monetization analysis for the specific chat

## LLM Analysis Format

The `llm_analysis_data.json` file is specially formatted for efficient analysis by Large Language Models, with:

- Aggregated keyword frequencies across all chats
- High-value conversations with significant monetization indicators
- Potential opportunities ranked by frequency
- Structured data format optimized for prompt context

## Monetization Analysis

The analysis identifies opportunities in these categories:

1. **Product Opportunities**
   - Purchase intent signals
   - Product recommendations and requests
   - Product comparisons and preferences

2. **Service Needs**
   - Professional service requests
   - Help-seeking behavior
   - Recurring service requirements

3. **Marketing Insights**
   - Sentiment analysis
   - Brand mentions and preferences
   - Feature requests and pain points

## Implementation Details

This project consists of several Python scripts:

- `extract_whatsapp_data.py`: User-friendly entry point script
- `whatsapp_mcp_extractor.py`: Main implementation with MCP integration
- `whatsapp_data_extractor_mcp.py`: Alternate implementation with more detailed MCP parsing
- `whatsapp_data_extractor.py`: Reference implementation with placeholder functions

## Next Steps for LLM Analysis

After running the extraction, you can:

1. Use the `llm_analysis_data.json` file as input for an LLM
2. Create prompts that help the LLM identify:
   - Top product/service monetization opportunities
   - Market gaps based on expressed needs
   - Audience interests and sentiment patterns
   - Potential business models based on conversation patterns

## Privacy and Security Considerations

This tool processes WhatsApp chat data locally. Consider these guidelines:

- Only analyze data you have permission to use
- Respect privacy and avoid sharing personal conversations
- Focus on aggregate patterns rather than individual messages
- Consider anonymizing data before deeper analysis
- Use insights for value creation, not exploitation

## Troubleshooting

If you encounter issues:

1. Ensure the WhatsApp MCP server is running
2. Verify your WhatsApp Web session is active
3. Check the extraction logs for error messages
4. Try limiting the extraction scope with `--max-chats` or `--max-history`
5. If processing large datasets, consider freeing up system memory
