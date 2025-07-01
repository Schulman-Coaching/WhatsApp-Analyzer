# Quick Start Guide - WhatsApp Analyzer

## 🚀 One-Command Installation

```bash
# Clone and setup automatically
git clone https://github.com/Schulman-Coaching/WhatsApp-Analyzer.git
cd WhatsApp-Analyzer
python setup.py
```

## 📋 Manual Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/Schulman-Coaching/WhatsApp-Analyzer.git
cd WhatsApp-Analyzer
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
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

### 5. Configure (Optional)
```bash
# Generate config file
python mcp_config.py
cp mcp_config_sample.json mcp_config.json
# Edit mcp_config.json with your settings
```

## 🎯 Quick Usage

### Basic Extraction
```bash
python extract_whatsapp_data.py
```

### Advanced Extraction
```bash
# Custom MCP server
python whatsapp_mcp_extractor.py --mcp-endpoint http://localhost:3000

# Limit extraction
python whatsapp_mcp_extractor.py --max-chats 10 --max-history 24

# WebSocket connection
python whatsapp_mcp_extractor.py --mcp-connection websocket
```

## 📁 What You Get

After installation, you'll have:
- **Production-ready MCP client** with rate limiting and error handling
- **WhatsApp-specific tools** for chat and message extraction
- **Configuration management** via JSON files or environment variables
- **Comprehensive documentation** and examples
- **Test suite** for validation

## 🔧 Prerequisites

- Python 3.8+ (recommended: 3.9+)
- WhatsApp MCP server running
- WhatsApp Web access

## 📚 Documentation

- `README.md` - Main documentation
- `INSTALLATION.md` - Detailed installation guide
- `MCP_CLIENT_DOCUMENTATION.md` - API reference

## 🆘 Need Help?

1. Run the test suite: `python test_mcp_client.py`
2. Check the detailed installation guide: `INSTALLATION.md`
3. Review the configuration: `mcp_config.json`
4. Ensure your MCP server is running

## 🎉 Success!

If everything works, you should see:
```
✅ All tests passed! MCP client infrastructure is ready.
```

Now you can start extracting and analyzing your WhatsApp data for monetization opportunities!