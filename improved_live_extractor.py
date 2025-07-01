#!/usr/bin/env python3
"""
Improved Live WhatsApp Data Extractor

This script properly parses the WhatsApp MCP server responses and extracts
real monetization opportunities from actual WhatsApp data.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

from mcp_stdio_client import MCPStdioClient


class ImprovedLiveExtractor:
    """Improved WhatsApp data extractor with proper data parsing"""
    
    def __init__(self):
        self.client = None
        self.output_dir = "live_extracted_data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.server_path = r"C:\Users\elie\OneDrive\Documents\Cline\MCP\whatsapp-mcp\whatsapp-mcp-server\main.py"
        
    def parse_mcp_response(self, result: Dict[str, Any]) -> Any:
        """Parse MCP server response format"""
        if isinstance(result, dict):
            if result.get("isError"):
                error_msg = result.get("content", "Unknown error")
                print(f"❌ Server error: {error_msg}")
                return None
            else:
                content = result.get("content", "")
                if isinstance(content, str):
                    try:
                        # Try to parse as JSON
                        return json.loads(content)
                    except json.JSONDecodeError:
                        # If not JSON, return as string
                        return content
                else:
                    return content
        return result
    
    def parse_chat_data(self, raw_chats: List[Any]) -> List[Dict[str, Any]]:
        """Parse raw chat data from MCP server"""
        parsed_chats = []
        
        for raw_chat in raw_chats:
            if isinstance(raw_chat, dict) and "text" in raw_chat:
                # Extract JSON from text field
                try:
                    chat_data = json.loads(raw_chat["text"])
                    parsed_chats.append(chat_data)
                except json.JSONDecodeError:
                    print(f"⚠️ Could not parse chat data: {raw_chat}")
            elif isinstance(raw_chat, dict):
                # Already parsed
                parsed_chats.append(raw_chat)
        
        return parsed_chats
    
    async def connect(self) -> bool:
        """Connect to WhatsApp MCP server"""
        try:
            print("🚀 Connecting to WhatsApp MCP server...")
            
            self.client = MCPStdioClient(self.server_path)
            
            if not await self.client.start():
                return False
            
            await asyncio.sleep(1)
            
            if not await self.client.initialize():
                return False
            
            print("✅ Connected to WhatsApp MCP server")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def extract_chats(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Extract and parse WhatsApp chats"""
        try:
            print(f"📱 Extracting {limit} chats...")
            
            result = await self.client.call_tool("list_chats", {
                "limit": limit,
                "page": 0,
                "include_last_message": True,
                "sort_by": "last_active"
            })
            
            # Parse the response
            parsed_result = self.parse_mcp_response(result)
            if parsed_result is None:
                return []
            
            # Handle different response formats
            if isinstance(parsed_result, list):
                chats = self.parse_chat_data(parsed_result)
            elif isinstance(parsed_result, dict) and "chats" in parsed_result:
                chats = self.parse_chat_data(parsed_result["chats"])
            else:
                print(f"⚠️ Unexpected response format: {type(parsed_result)}")
                return []
            
            print(f"✅ Successfully parsed {len(chats)} chats")
            
            # Save parsed chats
            self.save_json(chats, "parsed_chats.json")
            
            return chats
            
        except Exception as e:
            print(f"❌ Error extracting chats: {e}")
            return []
    
    async def extract_messages(self, chat_jid: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Extract messages from a specific chat"""
        try:
            print(f"💬 Extracting messages from {chat_jid[:30]}...")
            
            result = await self.client.call_tool("list_messages", {
                "chat_jid": chat_jid,
                "limit": limit,
                "page": 0,
                "include_context": True,
                "context_before": 1,
                "context_after": 1
            })
            
            # Parse the response
            parsed_result = self.parse_mcp_response(result)
            if parsed_result is None:
                return []
            
            # Handle different response formats
            if isinstance(parsed_result, list):
                messages = parsed_result
            elif isinstance(parsed_result, dict) and "messages" in parsed_result:
                messages = parsed_result["messages"]
            else:
                messages = []
            
            print(f"✅ Extracted {len(messages)} messages")
            return messages
            
        except Exception as e:
            print(f"❌ Error extracting messages: {e}")
            return []
    
    def save_json(self, data: Any, filename: str) -> str:
        """Save data to JSON file"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved to {filepath}")
        return filepath
    
    def analyze_real_data(self, chats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze real WhatsApp data for monetization opportunities"""
        print("🔍 Analyzing REAL WhatsApp data for monetization opportunities...")
        
        # Import analysis functions
        from whatsapp_mcp_extractor import identify_monetization_keywords
        
        analysis = {
            "extraction_time": datetime.now().isoformat(),
            "total_chats": len(chats),
            "total_messages": 0,
            "monetization_keywords": {
                "product_opportunities": {},
                "service_needs": {},
                "marketing_insights": {}
            },
            "high_value_chats": [],
            "real_opportunities": [],
            "sample_messages": []
        }
        
        for chat in chats:
            chat_name = chat.get("name", "Unknown Chat")
            chat_jid = chat.get("jid", "")
            
            # Analyze last message for immediate insights
            last_message = chat.get("last_message", "")
            messages = chat.get("messages", [])
            
            # Count total messages
            analysis["total_messages"] += len(messages)
            if last_message:
                analysis["total_messages"] += 1
            
            chat_indicators = 0
            chat_opportunities = []
            
            # Analyze last message (most recent activity)
            if last_message:
                keywords = identify_monetization_keywords(last_message)
                
                if any(keywords.values()):
                    chat_indicators += 1
                    
                    # Create opportunity from last message
                    opportunity = {
                        "chat_name": chat_name,
                        "message": last_message[:200] + "..." if len(last_message) > 200 else last_message,
                        "keywords": keywords,
                        "timestamp": chat.get("last_message_time", ""),
                        "type": "recent_activity"
                    }
                    chat_opportunities.append(opportunity)
                    analysis["real_opportunities"].append(opportunity)
                    
                    # Count keywords globally
                    for category in ["products", "services", "marketing"]:
                        for keyword in keywords[category]:
                            if category == "products":
                                key = "product_opportunities"
                            elif category == "services":
                                key = "service_needs"
                            else:
                                key = "marketing_insights"
                            
                            if keyword not in analysis["monetization_keywords"][key]:
                                analysis["monetization_keywords"][key][keyword] = 0
                            analysis["monetization_keywords"][key][keyword] += 1
            
            # Analyze extracted messages
            for message in messages:
                text = ""
                if isinstance(message, dict):
                    text = (message.get("text") or 
                           message.get("content") or 
                           message.get("body") or "")
                elif isinstance(message, str):
                    text = message
                
                if text:
                    keywords = identify_monetization_keywords(text)
                    
                    if any(keywords.values()):
                        chat_indicators += 1
                        
                        opportunity = {
                            "chat_name": chat_name,
                            "message": text[:200] + "..." if len(text) > 200 else text,
                            "keywords": keywords,
                            "timestamp": message.get("timestamp", ""),
                            "type": "historical_message"
                        }
                        chat_opportunities.append(opportunity)
                        analysis["real_opportunities"].append(opportunity)
                        
                        # Count keywords globally
                        for category in ["products", "services", "marketing"]:
                            for keyword in keywords[category]:
                                if category == "products":
                                    key = "product_opportunities"
                                elif category == "services":
                                    key = "service_needs"
                                else:
                                    key = "marketing_insights"
                                
                                if keyword not in analysis["monetization_keywords"][key]:
                                    analysis["monetization_keywords"][key][keyword] = 0
                                analysis["monetization_keywords"][key][keyword] += 1
            
            # Mark high-value chats
            if chat_indicators >= 1:  # Lower threshold since we have real data
                analysis["high_value_chats"].append({
                    "chat_name": chat_name,
                    "chat_jid": chat_jid,
                    "monetization_indicators": chat_indicators,
                    "opportunities": chat_opportunities[:3],  # Top 3 opportunities
                    "last_activity": chat.get("last_message_time", "")
                })
        
        return analysis
    
    async def run_real_extraction(self, max_chats: int = 10, max_messages_per_chat: int = 20):
        """Run extraction with real WhatsApp data"""
        print("🎯 REAL WhatsApp Data Extraction & Analysis")
        print("=" * 60)
        
        try:
            # Connect
            if not await self.connect():
                return False
            
            # Extract chats
            chats = await self.extract_chats(max_chats)
            if not chats:
                return False
            
            # Show what we found
            print(f"\n📋 REAL CHATS FOUND ({len(chats)}):")
            for i, chat in enumerate(chats):
                name = chat.get("name", "Unknown")
                last_msg = chat.get("last_message", "")[:50] + "..." if len(chat.get("last_message", "")) > 50 else chat.get("last_message", "")
                print(f"  {i+1}. {name}")
                print(f"     Last: {last_msg}")
            
            # Extract some messages for context (optional)
            print(f"\n💬 Extracting recent messages for context...")
            for i, chat in enumerate(chats[:3]):  # Only first 3 for demo
                chat_jid = chat.get("jid", "")
                if chat_jid:
                    messages = await self.extract_messages(chat_jid, max_messages_per_chat)
                    chat["messages"] = messages
                    await asyncio.sleep(1)  # Rate limiting
            
            # Save complete data
            complete_data = {
                "extraction_metadata": {
                    "extraction_time": datetime.now().isoformat(),
                    "total_chats": len(chats),
                    "extractor_version": "improved_v1.0",
                    "data_source": "real_whatsapp"
                },
                "chats": chats
            }
            
            self.save_json(complete_data, "real_whatsapp_data.json")
            
            # Analyze for monetization
            analysis = self.analyze_real_data(chats)
            self.save_json(analysis, "real_monetization_analysis.json")
            
            # Print results
            self.print_real_results(analysis)
            
            return True
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            if self.client:
                await self.client.close()
    
    def print_real_results(self, analysis: Dict[str, Any]):
        """Print analysis of real WhatsApp data"""
        print("\n" + "=" * 60)
        print("🎉 REAL DATA ANALYSIS COMPLETED!")
        print("=" * 60)
        
        print(f"📊 Real chats analyzed: {analysis['total_chats']}")
        print(f"💬 Real messages processed: {analysis['total_messages']}")
        print(f"🎯 High-value chats: {len(analysis['high_value_chats'])}")
        print(f"💰 Monetization opportunities found: {len(analysis['real_opportunities'])}")
        
        # Show real keywords found
        print("\n🔍 REAL MONETIZATION KEYWORDS DISCOVERED:")
        
        for category, keywords in analysis["monetization_keywords"].items():
            if keywords:
                print(f"\n{category.replace('_', ' ').title()}:")
                sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
                for keyword, count in sorted_keywords[:5]:
                    print(f"  • '{keyword}': {count} mentions")
        
        # Show high-value chats with real examples
        if analysis["high_value_chats"]:
            print(f"\n🏆 HIGH-VALUE CHATS WITH REAL OPPORTUNITIES:")
            for chat in analysis["high_value_chats"][:3]:
                print(f"\n📱 {chat['chat_name']}:")
                print(f"   Indicators: {chat['monetization_indicators']}")
                for opp in chat["opportunities"][:2]:
                    print(f"   💡 {opp['message'][:80]}...")
                    if opp['keywords']['products']:
                        print(f"      Products: {', '.join(opp['keywords']['products'][:3])}")
                    if opp['keywords']['services']:
                        print(f"      Services: {', '.join(opp['keywords']['services'][:3])}")
        
        print(f"\n💾 Real data saved to: {os.path.abspath(self.output_dir)}")
        print("📁 Files with REAL WhatsApp data:")
        print("  • real_whatsapp_data.json - Complete real chat data")
        print("  • real_monetization_analysis.json - Real business opportunities")
        print("  • parsed_chats.json - Parsed chat information")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract REAL WhatsApp data for monetization analysis")
    parser.add_argument("--max-chats", type=int, default=5, help="Maximum chats to process")
    parser.add_argument("--max-messages", type=int, default=20, help="Maximum messages per chat")
    
    args = parser.parse_args()
    
    extractor = ImprovedLiveExtractor()
    
    try:
        success = await extractor.run_real_extraction(args.max_chats, args.max_messages)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️ Extraction interrupted")
        if extractor.client:
            await extractor.client.close()
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        if extractor.client:
            await extractor.client.close()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))