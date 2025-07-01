# WhatsApp Analyzer Installation Guide

This guide will help you install and set up the WhatsApp Analyzer with MCP client infrastructure.

## Prerequisites

- **Python 3.8 or higher** (Python 3.9+ recommended)
- **Git** (for cloning the repository)
- **WhatsApp MCP Server** (running separately)
- **WhatsApp Web** access

## Quick Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Schulman-Coaching/WhatsApp-Analyzer.git
cd WhatsApp-Analyzer
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Test Installation

```bash
python test_mcp_client.py
```

### 5. Configure MCP Client

```bash
# Generate sample configuration
python mcp_config.py

# Copy and customize configuration
cp mcp_config_sample.json mcp_config.json
# Edit mcp_config.json with your settings
```

## Detailed Installation Steps

### Step 1: System Requirements

Ensure you have the required software:

#### Python Installation
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: Use Homebrew: `brew install python3`
- **Linux**: Use package manager: `sudo apt-get install python3 python3-pip`

Verify installation:
```bash
python --version  # Should be 3.8+
pip --version
```

#### Git Installation
- **Windows**: Download from [git-scm.com](https://git-scm.com/download/win)
- **macOS**: Use Homebrew: `brew install git`
- **Linux**: Use package manager: `sudo apt-get install git`

### Step 2: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Schulman-Coaching/WhatsApp-Analyzer.git
cd WhatsApp-Analyzer

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configuration

#### Generate Configuration File
```bash
python mcp_config.py
```

This creates `mcp_config_sample.json`. Copy it to `mcp_config.json`:

```bash
# Windows:
copy mcp_config_sample.json mcp_config.json
# macOS/Linux:
cp mcp_config_sample.json mcp_config.json
```

#### Edit Configuration
Edit `mcp_config.json` with your settings:

```json
{
  "whatsapp": {
    "server": {
      "name": "github.com/lharries/whatsapp-mcp",
      "endpoint": "http://localhost:3000",
      "connection_type": "sse",
      "auth_token": null,
      "timeout": 60,
      "max_retries": 5
    },
    "rate_limits": {
      "messages_per_minute": 60,
      "chats_per_minute": 30,
      "requests_per_second": 2
    },
    "auto_authenticate": false,
    "phone_number": null
  }
}
```

#### Environment Variables (Alternative)
Instead of config file, you can use environment variables:

```bash
# Windows:
set MCP_WHATSAPP_ENDPOINT=http://localhost:3000
set MCP_WHATSAPP_CONNECTION_TYPE=sse

# macOS/Linux:
export MCP_WHATSAPP_ENDPOINT=http://localhost:3000
export MCP_WHATSAPP_CONNECTION_TYPE=sse
```

### Step 4: WhatsApp MCP Server Setup

You need a WhatsApp MCP server running. If you have one:

1. Start your WhatsApp MCP server
2. Update the endpoint in `mcp_config.json`
3. Ensure WhatsApp Web is accessible

### Step 5: Test Installation

Run the test suite:

```bash
python test_mcp_client.py
```

Expected output:
```
✓ All MCP modules imported successfully
✓ Configuration loaded successfully
✓ Sync client created
✓ Async client created
✓ All tests passed! MCP client infrastructure is ready.
```

## Usage

### Basic Usage

```bash
# Extract all chats
python extract_whatsapp_data.py

# Extract with limits
python extract_whatsapp_data.py --max-chats 10 --max-history 24

# Use advanced MCP extractor
python whatsapp_mcp_extractor.py --mcp-endpoint http://localhost:3000
```

### Advanced Usage

```bash
# Custom MCP server
python whatsapp_mcp_extractor.py --mcp-endpoint http://your-server:3000

# WebSocket connection
python whatsapp_mcp_extractor.py --mcp-connection websocket

# With authentication
python whatsapp_mcp_extractor.py --auth-token your-token-here
```

## Troubleshooting

### Common Issues

#### 1. Python Version Error
```
Error: Python 3.8+ required
```
**Solution**: Upgrade Python to 3.8 or higher.

#### 2. Module Import Error
```
ModuleNotFoundError: No module named 'aiohttp'
```
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

#### 3. MCP Connection Error
```
Failed to initialize WhatsApp MCP client
```
**Solutions**:
- Ensure MCP server is running
- Check endpoint URL in configuration
- Verify network connectivity

#### 4. Virtual Environment Issues
```
'venv' is not recognized as an internal or external command
```
**Solution**: Use full Python path:
```bash
python -m venv venv
```

#### 5. Permission Errors (Windows)
```
Access denied
```
**Solution**: Run as administrator or check file permissions.

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set environment variable:
```bash
# Windows:
set PYTHONPATH=.
set LOG_LEVEL=DEBUG

# macOS/Linux:
export PYTHONPATH=.
export LOG_LEVEL=DEBUG
```

### Getting Help

1. **Check Logs**: Look for error messages in console output
2. **Test Configuration**: Run `python test_mcp_client.py`
3. **Verify Dependencies**: Run `pip list` to check installed packages
4. **Check MCP Server**: Ensure your WhatsApp MCP server is running
5. **Review Documentation**: See `MCP_CLIENT_DOCUMENTATION.md`

## Development Setup

For development work:

```bash
# Install development dependencies
pip install pytest pytest-asyncio black flake8

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

## Uninstallation

To remove the installation:

```bash
# Deactivate virtual environment
deactivate

# Remove directory
cd ..
rm -rf WhatsApp-Analyzer  # macOS/Linux
rmdir /s WhatsApp-Analyzer  # Windows
```

## Next Steps

After successful installation:

1. **Configure MCP Server**: Set up your WhatsApp MCP server endpoint
2. **Test Connection**: Run a small extraction to verify everything works
3. **Customize Settings**: Adjust rate limits and other settings as needed
4. **Run Analysis**: Start extracting and analyzing your WhatsApp data

For detailed usage instructions, see the main `README.md` file.