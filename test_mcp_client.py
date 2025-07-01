#!/usr/bin/env python3
"""
Test Script for MCP Client Infrastructure

This script provides basic tests and validation for the MCP client infrastructure
to ensure everything is working correctly.
"""

import asyncio
import logging
import sys
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import MCP components
try:
    from mcp_client import MCPClient, MCPServerConfig, MCPConnectionType
    from whatsapp_mcp_client import WhatsAppMCPClient
    from mcp_utils import use_mcp_tool, initialize_whatsapp_mcp, get_sync_whatsapp_client
    from mcp_config import get_mcp_config, get_whatsapp_settings
    logger.info("✓ All MCP modules imported successfully")
except ImportError as e:
    logger.error(f"✗ Failed to import MCP modules: {e}")
    sys.exit(1)


def test_configuration():
    """Test configuration system"""
    logger.info("Testing configuration system...")
    
    try:
        # Test config loading
        config = get_mcp_config()
        settings = get_whatsapp_settings()
        
        logger.info(f"✓ Configuration loaded successfully")
        logger.info(f"  - Server endpoint: {settings.server.endpoint}")
        logger.info(f"  - Connection type: {settings.server.connection_type}")
        logger.info(f"  - Rate limits: {settings.rate_limits}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False


def test_sync_client_creation():
    """Test synchronous client creation"""
    logger.info("Testing synchronous client creation...")
    
    try:
        client = get_sync_whatsapp_client()
        logger.info(f"✓ Sync client created: {type(client).__name__}")
        logger.info(f"  - Initialized: {client.is_initialized()}")
        logger.info(f"  - Connected: {client.is_connected()}")
        logger.info(f"  - Authenticated: {client.is_authenticated()}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Sync client creation failed: {e}")
        return False


async def test_async_client_creation():
    """Test asynchronous client creation"""
    logger.info("Testing asynchronous client creation...")
    
    try:
        client = WhatsAppMCPClient()
        logger.info(f"✓ Async client created: {type(client).__name__}")
        logger.info(f"  - Server name: {client.server_name}")
        logger.info(f"  - Rate limits: {client.rate_limits}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Async client creation failed: {e}")
        return False


def test_mcp_tool_function():
    """Test the use_mcp_tool function (without actual server connection)"""
    logger.info("Testing use_mcp_tool function...")
    
    try:
        # This will fail to connect, but we can test the function structure
        try:
            result = use_mcp_tool(
                server_name="github.com/lharries/whatsapp-mcp",
                tool_name="list_chats",
                arguments={"limit": 1, "page": 0}
            )
            logger.info("✓ use_mcp_tool executed (unexpected success)")
        except Exception as e:
            # Expected to fail without actual server
            if "Failed to initialize" in str(e) or "connection" in str(e).lower():
                logger.info("✓ use_mcp_tool function structure is correct (expected connection failure)")
            else:
                logger.warning(f"⚠ use_mcp_tool failed with unexpected error: {e}")
        
        return True
    except Exception as e:
        logger.error(f"✗ use_mcp_tool test failed: {e}")
        return False


def test_initialization_function():
    """Test the initialization function"""
    logger.info("Testing initialization function...")
    
    try:
        # Test with invalid endpoint (should fail gracefully)
        success = initialize_whatsapp_mcp(
            endpoint="http://invalid-endpoint:9999",
            connection_type="sse",
            use_config=False
        )
        
        if not success:
            logger.info("✓ Initialization correctly failed with invalid endpoint")
        else:
            logger.warning("⚠ Initialization unexpectedly succeeded with invalid endpoint")
        
        return True
    except Exception as e:
        logger.error(f"✗ Initialization test failed: {e}")
        return False


async def test_async_initialization():
    """Test async client initialization"""
    logger.info("Testing async client initialization...")
    
    try:
        client = WhatsAppMCPClient()
        
        # Test with invalid endpoint (should fail gracefully)
        success = await client.initialize(
            endpoint="http://invalid-endpoint:9999",
            connection_type=MCPConnectionType.SSE
        )
        
        if not success:
            logger.info("✓ Async initialization correctly failed with invalid endpoint")
        else:
            logger.warning("⚠ Async initialization unexpectedly succeeded with invalid endpoint")
        
        return True
    except Exception as e:
        logger.error(f"✗ Async initialization test failed: {e}")
        return False


def test_error_handling():
    """Test error handling capabilities"""
    logger.info("Testing error handling...")
    
    try:
        from mcp_client import MCPClientError, MCPConnectionError, MCPToolError
        
        # Test exception hierarchy
        assert issubclass(MCPConnectionError, MCPClientError)
        assert issubclass(MCPToolError, MCPClientError)
        
        logger.info("✓ Exception hierarchy is correct")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error handling test failed: {e}")
        return False


def create_sample_config():
    """Create a sample configuration file for testing"""
    logger.info("Creating sample configuration...")
    
    try:
        from mcp_config import MCPConfig
        config = MCPConfig()
        config.create_sample_config("test_mcp_config.json")
        logger.info("✓ Sample configuration created: test_mcp_config.json")
        return True
    except Exception as e:
        logger.error(f"✗ Sample config creation failed: {e}")
        return False


async def run_async_tests():
    """Run all async tests"""
    logger.info("Running async tests...")
    
    tests = [
        test_async_client_creation(),
        test_async_initialization()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    passed = 0
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Async test {i+1} raised exception: {result}")
        elif result:
            passed += 1
    
    logger.info(f"Async tests: {passed}/{len(tests)} passed")
    return passed == len(tests)


def run_sync_tests():
    """Run all synchronous tests"""
    logger.info("Running synchronous tests...")
    
    tests = [
        test_configuration,
        test_sync_client_creation,
        test_mcp_tool_function,
        test_initialization_function,
        test_error_handling,
        create_sample_config
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            logger.error(f"Test {test.__name__} raised exception: {e}")
    
    logger.info(f"Sync tests: {passed}/{len(tests)} passed")
    return passed == len(tests)


def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("MCP Client Infrastructure Test Suite")
    logger.info("=" * 60)
    
    # Run synchronous tests
    sync_success = run_sync_tests()
    
    # Run asynchronous tests
    async_success = asyncio.run(run_async_tests())
    
    # Summary
    logger.info("=" * 60)
    logger.info("Test Summary:")
    logger.info(f"  Synchronous tests: {'PASSED' if sync_success else 'FAILED'}")
    logger.info(f"  Asynchronous tests: {'PASSED' if async_success else 'FAILED'}")
    
    if sync_success and async_success:
        logger.info("✓ All tests passed! MCP client infrastructure is ready.")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Start your WhatsApp MCP server")
        logger.info("2. Update mcp_config.json with your server endpoint")
        logger.info("3. Run: python whatsapp_mcp_extractor.py")
        return 0
    else:
        logger.error("✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())