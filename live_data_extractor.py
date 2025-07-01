#!/usr/bin/env python3
"""
Live WhatsApp Data Extractor

This script connects to the actual WhatsApp MCP server and extracts real data
from your WhatsApp chats for monetization analysis.
"""

import asyncio
import json
import os
import sys
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import our MCP client infrastructure
from mcp_client import MCPClient, MCPServerConfig, MCPConnectionType
from mcp_config import get_whatsapp_settings


class LiveWhatsAppExtractor:
    """Live WhatsApp data extractor using actual MCP server"""
    
    def __init__(self):
        self.mcp_process = None
        self.client = MCPClient()
        self.server_name = "whatsapp-live"
        self.output_dir = "live_extracted_data"
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def start_mcp_server(self) -> bool:
        """Start the WhatsApp MCP server process"""
        try:
            print("🚀 Starting WhatsApp MCP server...")
            
            # Get the server path from config
            settings = get_whatsapp_settings()
            server_path = settings.server.endpoint
            
            # Start the MCP server process
            self.mcp_process = await asyncio.create_subprocess_exec(
                sys.executable, server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            print("✅ MCP server process started")
            
            # Configure the MCP client
            config = MCPServerConfig(
                name=self.server_name,
                connection_type=MCPConnectionType.STDIO,
                endpoint=server_path,
                timeout=120,  # Longer timeout for real operations
                max_retries=3,
                retry_delay=2.0
            )
            
            self.client.add_server(config)
            
            # Connect to the server
            print("🔗 Connecting to MCP server...")
            success = await self.client.connect(self.server_name)
            
            if success:
                print("✅ Successfully connected to WhatsApp MCP server")
                return True
            else:
                print("❌ Failed to connect to MCP server")
                return False
                
        except Exception as e:
            print(f"❌ Error starting MCP server: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test the MCP server connection"""
        try:
            print("🧪 Testing MCP server connection...")
            
            # Try to list available tools
            result = await self.client.execute_tool(
                self.server_name,
                "list_tools",
                {}
            )
            
            print("✅ Connection test successful")
            print(f"Available tools: {len(result.get('tools', []))}")
            return True
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    async def extract_live_chats(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Extract real chats from WhatsApp"""
        try:
            print(f"📱 Extracting {limit} chats from WhatsApp...")
            
            result = await self.client.execute_tool(
                self.server_name,
                "list_chats",
                {
                    "limit": limit,
                    "page": 0,
                    "include_last_message": True,
                    "sort_by": "last_active"
                }
            )
            
            chats = result if isinstance(result, list) else result.get("chats", [])
            print(f"✅ Successfully extracted {len(chats)} chats")
            
            # Save chats data
            self.save_json(chats, "live_chats.json")
            
            return chats
            
        except Exception as e:
            print(f"❌ Error extracting chats: {e}")
            return []
    
    async def extract_live_messages(self, chat_jid: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Extract real messages from a specific chat"""
        try:
            print(f"💬 Extracting {limit} messages from chat {chat_jid}...")
            
            result = await self.client.execute_tool(
                self.server_name,
                "list_messages",
                {
                    "chat_jid": chat_jid,
                    "limit": limit,
                    "page": 0,
                    "include_context": True,
                    "context_before": 1,
                    "context_after": 1
                }
            )
            
            messages = result if isinstance(result, list) else result.get("messages", [])
            print(f"✅ Successfully extracted {len(messages)} messages")
            
            return messages
            
        except Exception as e:
            print(f"❌ Error extracting messages from {chat_jid}: {e}")
            return []
    
    async def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Search for contacts"""
        try:
            print(f"🔍 Searching contacts for: {query}")
            
            result = await self.client.execute_tool(
                self.server_name,
                "search_contacts",
                {"query": query}
            )
            
            contacts = result if isinstance(result, list) else result.get("contacts", [])
            print(f"✅ Found {len(contacts)} contacts")
            
            return contacts
            
        except Exception as e:
            print(f"❌ Error searching contacts: {e}")
            return []
    
    def save_json(self, data: Any, filename: str) -> str:
        """Save data to JSON file"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved data to {filepath}")
        return filepath
    
    def analyze_monetization_opportunities(self, chats_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze real chat data for monetization opportunities"""
        print("🔍 Analyzing monetization opportunities...")
        
        # Import the analysis functions from our existing code
        from whatsapp_mcp_extractor import (
            identify_monetization_keywords,
            process_message_for_monetization
        )
        
        opportunities = {
            "total_chats": len(chats_data),
            "total_messages": 0,
            "monetization_indicators": {
                "product_opportunities": {},
                "service_needs": {},
                "marketing_insights": {}
            },
            "high_value_chats": [],
            "extraction_time": datetime.now().isoformat()
        }
        
        for chat in chats_data:
            chat_name = chat.get("name", "Unknown")
            messages = chat.get("messages", [])
            opportunities["total_messages"] += len(messages)
            
            chat_indicators = []
            
            for message in messages:
                # Extract text from message
                text = ""
                if isinstance(message, dict):
                    text = message.get("text", message.get("content", ""))
                elif isinstance(message, str):
                    text = message
                
                if text:
                    # Analyze for monetization keywords
                    keywords = identify_monetization_keywords(text)
                    
                    # Count keywords by category
                    for category in ["products", "services", "marketing"]:
                        category_key = f"{category.rstrip('s')}_opportunities" if category != "marketing" else "marketing_insights"
                        
                        for keyword in keywords[category]:
                            if keyword not in opportunities["monetization_indicators"][category_key]:
                                opportunities["monetization_indicators"][category_key][keyword] = 0
                            opportunities["monetization_indicators"][category_key][keyword] += 1
                    
                    # If message has indicators, add to chat indicators
                    if any(keywords.values()):
                        chat_indicators.append({
                            "text": text[:100] + "..." if len(text) > 100 else text,
                            "keywords": keywords
                        })
            
            # If chat has significant indicators, mark as high-value
            if len(chat_indicators) >= 3:
                opportunities["high_value_chats"].append({
                    "chat_name": chat_name,
                    "indicator_count": len(chat_indicators),
                    "sample_indicators": chat_indicators[:5]  # Top 5 examples
                })
        
        return opportunities
    
    async def run_live_extraction(self, max_chats: int = 10, max_messages_per_chat: int = 50):
        """Run complete live data extraction and analysis"""
        print("🎯 Starting live WhatsApp data extraction...")
        print("=" * 60)
        
        try:
            # Start MCP server
            if not await self.start_mcp_server():
                return False
            
            # Wait a moment for server to fully initialize
            await asyncio.sleep(2)
            
            # Test connection
            if not await self.test_connection():
                return False
            
            # Extract chats
            chats = await self.extract_live_chats(max_chats)
            if not chats:
                print("❌ No chats extracted")
                return False
            
            # Extract messages for each chat
            print(f"📱 Processing {len(chats)} chats...")
            for i, chat in enumerate(chats):
                chat_jid = chat.get("jid", "")
                chat_name = chat.get("name", f"Chat {i+1}")
                
                if chat_jid:
                    print(f"Processing chat {i+1}/{len(chats)}: {chat_name}")
                    messages = await self.extract_live_messages(chat_jid, max_messages_per_chat)
                    chat["messages"] = messages
                    
                    # Rate limiting - be respectful to WhatsApp
                    await asyncio.sleep(1)
            
            # Save complete dataset
            complete_data = {
                "chats": chats,
                "extraction_metadata": {
                    "extraction_time": datetime.now().isoformat(),
                    "total_chats": len(chats),
                    "total_messages": sum(len(chat.get("messages", [])) for chat in chats)
                }
            }
            
            self.save_json(complete_data, "live_whatsapp_data.json")
            
            # Analyze for monetization opportunities
            opportunities = self.analyze_monetization_opportunities(chats)
            self.save_json(opportunities, "live_monetization_analysis.json")
            
            # Print summary
            print("\n" + "=" * 60)
            print("🎉 Live extraction completed successfully!")
            print("=" * 60)
            print(f"📊 Chats processed: {opportunities['total_chats']}")
            print(f"💬 Messages analyzed: {opportunities['total_messages']}")
            print(f"🎯 High-value chats: {len(opportunities['high_value_chats'])}")
            
            # Show top opportunities
            print("\n🔍 Top Monetization Keywords:")
            for category, keywords in opportunities["monetization_indicators"].items():
                if keywords:
                    print(f"\n{category.replace('_', ' ').title()}:")
                    sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
                    for keyword, count in sorted_keywords[:5]:
                        print(f"  - '{keyword}': {count} mentions")
            
            print(f"\n💾 Data saved to: {os.path.abspath(self.output_dir)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during live extraction: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            if self.client:
                await self.client.disconnect_all()
            
            if self.mcp_process:
                self.mcp_process.terminate()
                await self.mcp_process.wait()
                
            print("🧹 Cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract live WhatsApp data for monetization analysis")
    parser.add_argument("--max-chats", type=int, default=10, help="Maximum number of chats to process")
    parser.add_argument("--max-messages", type=int, default=50, help="Maximum messages per chat")
    parser.add_argument("--search", type=str, help="Search for specific contacts first")
    
    args = parser.parse_args()
    
    extractor = LiveWhatsAppExtractor()
    
    try:
        if args.search:
            # Start server for search
            if await extractor.start_mcp_server():
                await asyncio.sleep(2)
                contacts = await extractor.search_contacts(args.search)
                extractor.save_json(contacts, f"search_results_{args.search}.json")
                await extractor.cleanup()
        else:
            # Run full extraction
            success = await extractor.run_live_extraction(args.max_chats, args.max_messages)
            return 0 if success else 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Extraction interrupted by user")
        await extractor.cleanup()
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        await extractor.cleanup()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))