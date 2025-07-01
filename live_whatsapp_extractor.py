#!/usr/bin/env python3
"""
Live WhatsApp Data Extractor - Production Version

This script connects to the actual WhatsApp MCP server and extracts real data
from your WhatsApp chats for monetization analysis.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

from mcp_stdio_client import MCPStdioClient


class LiveWhatsAppExtractor:
    """Production WhatsApp data extractor using real MCP server"""
    
    def __init__(self):
        self.client = None
        self.output_dir = "live_extracted_data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Server path from config
        self.server_path = r"C:\Users\elie\OneDrive\Documents\Cline\MCP\whatsapp-mcp\whatsapp-mcp-server\main.py"
        
    async def connect(self) -> bool:
        """Connect to WhatsApp MCP server"""
        try:
            print("🚀 Connecting to WhatsApp MCP server...")
            
            self.client = MCPStdioClient(self.server_path)
            
            # Start and initialize
            if not await self.client.start():
                print("❌ Failed to start MCP server")
                return False
            
            await asyncio.sleep(1)  # Wait for server startup
            
            if not await self.client.initialize():
                print("❌ Failed to initialize MCP connection")
                return False
            
            print("✅ Successfully connected to WhatsApp MCP server")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def extract_chats(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Extract real WhatsApp chats"""
        try:
            print(f"📱 Extracting {limit} most recent chats...")
            
            result = await self.client.call_tool("list_chats", {
                "limit": limit,
                "page": 0,
                "include_last_message": True,
                "sort_by": "last_active"
            })
            
            # Handle the response format
            if isinstance(result, dict):
                if result.get("isError"):
                    error_msg = result.get("content", "Unknown error")
                    print(f"❌ Error from server: {error_msg}")
                    return []
                else:
                    # Success case - extract content
                    content = result.get("content", [])
                    if isinstance(content, str):
                        try:
                            content = json.loads(content)
                        except json.JSONDecodeError:
                            print(f"⚠️ Could not parse content as JSON: {content}")
                            return []
                    
                    chats = content if isinstance(content, list) else []
                    print(f"✅ Successfully extracted {len(chats)} chats")
                    
                    # Save raw chats data
                    self.save_json(chats, "live_chats.json")
                    
                    return chats
            else:
                print(f"⚠️ Unexpected result format: {type(result)}")
                return []
                
        except Exception as e:
            print(f"❌ Error extracting chats: {e}")
            return []
    
    async def extract_messages(self, chat_jid: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Extract messages from a specific chat"""
        try:
            print(f"💬 Extracting {limit} messages from chat {chat_jid[:20]}...")
            
            result = await self.client.call_tool("list_messages", {
                "chat_jid": chat_jid,
                "limit": limit,
                "page": 0,
                "include_context": True,
                "context_before": 1,
                "context_after": 1
            })
            
            # Handle the response format
            if isinstance(result, dict):
                if result.get("isError"):
                    error_msg = result.get("content", "Unknown error")
                    print(f"❌ Error extracting messages: {error_msg}")
                    return []
                else:
                    content = result.get("content", [])
                    if isinstance(content, str):
                        try:
                            content = json.loads(content)
                        except json.JSONDecodeError:
                            print(f"⚠️ Could not parse messages as JSON")
                            return []
                    
                    messages = content if isinstance(content, list) else []
                    print(f"✅ Extracted {len(messages)} messages")
                    return messages
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error extracting messages: {e}")
            return []
    
    async def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Search for contacts"""
        try:
            print(f"🔍 Searching contacts for: '{query}'")
            
            result = await self.client.call_tool("search_contacts", {
                "query": query
            })
            
            if isinstance(result, dict):
                if result.get("isError"):
                    error_msg = result.get("content", "Unknown error")
                    print(f"❌ Search error: {error_msg}")
                    return []
                else:
                    content = result.get("content", [])
                    if isinstance(content, str):
                        try:
                            content = json.loads(content)
                        except json.JSONDecodeError:
                            return []
                    
                    contacts = content if isinstance(content, list) else []
                    print(f"✅ Found {len(contacts)} contacts")
                    return contacts
            else:
                return []
                
        except Exception as e:
            print(f"❌ Contact search failed: {e}")
            return []
    
    def save_json(self, data: Any, filename: str) -> str:
        """Save data to JSON file"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved to {filepath}")
        return filepath
    
    def analyze_monetization_opportunities(self, chats_with_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze real chat data for monetization opportunities"""
        print("🔍 Analyzing monetization opportunities in real data...")
        
        # Import analysis functions
        from whatsapp_mcp_extractor import identify_monetization_keywords
        
        analysis = {
            "extraction_time": datetime.now().isoformat(),
            "total_chats": len(chats_with_messages),
            "total_messages": 0,
            "monetization_keywords": {
                "product_opportunities": {},
                "service_needs": {},
                "marketing_insights": {}
            },
            "high_value_chats": [],
            "sample_messages": []
        }
        
        for chat in chats_with_messages:
            chat_name = chat.get("name", "Unknown Chat")
            chat_jid = chat.get("jid", "")
            messages = chat.get("messages", [])
            
            analysis["total_messages"] += len(messages)
            
            chat_indicators = 0
            chat_keywords = {"products": [], "services": [], "marketing": []}
            
            for message in messages:
                # Extract text from various possible fields
                text = ""
                if isinstance(message, dict):
                    text = (message.get("text") or 
                           message.get("content") or 
                           message.get("body") or "")
                elif isinstance(message, str):
                    text = message
                
                if text and len(text.strip()) > 0:
                    # Analyze for keywords
                    keywords = identify_monetization_keywords(text)
                    
                    # Count keywords
                    for category in ["products", "services", "marketing"]:
                        for keyword in keywords[category]:
                            chat_keywords[category].append(keyword)
                            
                            # Map to analysis structure
                            if category == "products":
                                key = "product_opportunities"
                            elif category == "services":
                                key = "service_needs"
                            else:
                                key = "marketing_insights"
                            
                            if keyword not in analysis["monetization_keywords"][key]:
                                analysis["monetization_keywords"][key][keyword] = 0
                            analysis["monetization_keywords"][key][keyword] += 1
                    
                    # If message has keywords, count as indicator
                    if any(keywords.values()):
                        chat_indicators += 1
                        
                        # Save sample messages
                        if len(analysis["sample_messages"]) < 20:
                            analysis["sample_messages"].append({
                                "chat_name": chat_name,
                                "text": text[:200] + "..." if len(text) > 200 else text,
                                "keywords": keywords
                            })
            
            # Mark high-value chats
            if chat_indicators >= 3:
                analysis["high_value_chats"].append({
                    "chat_name": chat_name,
                    "chat_jid": chat_jid,
                    "message_count": len(messages),
                    "monetization_indicators": chat_indicators,
                    "top_keywords": {
                        "products": list(set(chat_keywords["products"]))[:5],
                        "services": list(set(chat_keywords["services"]))[:5],
                        "marketing": list(set(chat_keywords["marketing"]))[:5]
                    }
                })
        
        return analysis
    
    async def run_full_extraction(self, max_chats: int = 10, max_messages_per_chat: int = 50):
        """Run complete live data extraction"""
        print("🎯 Starting LIVE WhatsApp Data Extraction")
        print("=" * 60)
        
        try:
            # Connect to server
            if not await self.connect():
                return False
            
            # Extract chats
            chats = await self.extract_chats(max_chats)
            if not chats:
                print("❌ No chats found or extraction failed")
                return False
            
            print(f"\n📋 Found {len(chats)} chats:")
            for i, chat in enumerate(chats[:5]):  # Show first 5
                name = chat.get("name", "Unknown")
                jid = chat.get("jid", "")[:30] + "..." if len(chat.get("jid", "")) > 30 else chat.get("jid", "")
                print(f"  {i+1}. {name} ({jid})")
            
            if len(chats) > 5:
                print(f"  ... and {len(chats) - 5} more")
            
            # Extract messages for each chat
            print(f"\n💬 Extracting messages from {len(chats)} chats...")
            
            for i, chat in enumerate(chats):
                chat_jid = chat.get("jid", "")
                chat_name = chat.get("name", f"Chat {i+1}")
                
                if chat_jid:
                    print(f"\nProcessing {i+1}/{len(chats)}: {chat_name}")
                    messages = await self.extract_messages(chat_jid, max_messages_per_chat)
                    chat["messages"] = messages
                    
                    # Rate limiting - be respectful
                    if i < len(chats) - 1:  # Don't sleep after last chat
                        await asyncio.sleep(2)
            
            # Save complete dataset
            complete_data = {
                "extraction_metadata": {
                    "extraction_time": datetime.now().isoformat(),
                    "total_chats": len(chats),
                    "total_messages": sum(len(chat.get("messages", [])) for chat in chats),
                    "extractor_version": "live_v1.0"
                },
                "chats": chats
            }
            
            self.save_json(complete_data, "live_whatsapp_complete.json")
            
            # Analyze for monetization
            analysis = self.analyze_monetization_opportunities(chats)
            self.save_json(analysis, "live_monetization_analysis.json")
            
            # Print results
            self.print_results(analysis)
            
            return True
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            if self.client:
                await self.client.close()
    
    def print_results(self, analysis: Dict[str, Any]):
        """Print extraction results"""
        print("\n" + "=" * 60)
        print("🎉 LIVE EXTRACTION COMPLETED!")
        print("=" * 60)
        
        print(f"📊 Total chats processed: {analysis['total_chats']}")
        print(f"💬 Total messages analyzed: {analysis['total_messages']}")
        print(f"🎯 High-value chats found: {len(analysis['high_value_chats'])}")
        
        # Show top keywords
        print("\n🔍 TOP MONETIZATION KEYWORDS FOUND:")
        
        for category, keywords in analysis["monetization_keywords"].items():
            if keywords:
                print(f"\n{category.replace('_', ' ').title()}:")
                sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
                for keyword, count in sorted_keywords[:5]:
                    print(f"  • '{keyword}': {count} mentions")
        
        # Show high-value chats
        if analysis["high_value_chats"]:
            print(f"\n🏆 HIGH-VALUE CHATS ({len(analysis['high_value_chats'])}):")
            for chat in analysis["high_value_chats"][:3]:
                print(f"  • {chat['chat_name']}: {chat['monetization_indicators']} indicators")
        
        print(f"\n💾 Data saved to: {os.path.abspath(self.output_dir)}")
        print("📁 Files created:")
        print("  • live_whatsapp_complete.json - Complete chat data")
        print("  • live_monetization_analysis.json - Business opportunity analysis")
        print("  • live_chats.json - Chat list")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract LIVE WhatsApp data for monetization analysis")
    parser.add_argument("--max-chats", type=int, default=10, help="Maximum chats to process (default: 10)")
    parser.add_argument("--max-messages", type=int, default=50, help="Maximum messages per chat (default: 50)")
    parser.add_argument("--search", type=str, help="Search for specific contacts")
    
    args = parser.parse_args()
    
    extractor = LiveWhatsAppExtractor()
    
    try:
        if args.search:
            # Search mode
            if await extractor.connect():
                contacts = await extractor.search_contacts(args.search)
                extractor.save_json(contacts, f"contact_search_{args.search}.json")
                print(f"Search results saved for '{args.search}'")
                await extractor.client.close()
        else:
            # Full extraction mode
            success = await extractor.run_full_extraction(args.max_chats, args.max_messages)
            return 0 if success else 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Extraction interrupted by user")
        if extractor.client:
            await extractor.client.close()
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if extractor.client:
            await extractor.client.close()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))