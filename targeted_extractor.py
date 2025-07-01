#!/usr/bin/env python3
"""
Targeted WhatsApp Chat Extractor

This script provides targeted extraction capabilities for specific high-value chats:
- Extract from specific chat names or JIDs
- Focus on community chats with concentrated business data
- Deep message history extraction for selected chats
- Enhanced filtering and analysis for targeted chats
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
import time

from mcp_stdio_client import MCPStdioClient


class TargetedExtractor:
    """Targeted WhatsApp data extractor for specific high-value chats"""
    
    def __init__(self):
        self.client = None
        self.output_dir = "targeted_extracted_data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.server_path = r"C:\Users\elie\OneDrive\Documents\Cline\MCP\whatsapp-mcp\whatsapp-mcp-server\main.py"
        
        # Rate limiting settings (more aggressive for targeted extraction)
        self.chat_delay = 1.0  # Faster since we're targeting specific chats
        self.message_delay = 0.5  # Faster message extraction
        
        # Target chat configuration
        self.target_chats = []
        self.chat_filters = {
            "community_keywords": ["group", "community", "neighborhood", "RBS", "team", "olot"],
            "business_keywords": ["property", "forex", "lawyers", "business", "professional"],
            "exclude_keywords": ["status", "broadcast"]
        }
    
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
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return content
                else:
                    return content
        return result
    
    def parse_chat_data(self, raw_chats: List[Any]) -> List[Dict[str, Any]]:
        """Parse raw chat data from MCP server"""
        parsed_chats = []
        
        for raw_chat in raw_chats:
            if isinstance(raw_chat, dict) and "text" in raw_chat:
                try:
                    chat_data = json.loads(raw_chat["text"])
                    parsed_chats.append(chat_data)
                except json.JSONDecodeError:
                    print(f"⚠️ Could not parse chat data")
            elif isinstance(raw_chat, dict):
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
    
    def is_high_value_chat(self, chat: Dict[str, Any]) -> bool:
        """Determine if a chat is high-value based on filters"""
        chat_name = chat.get("name", "").lower()
        
        # Exclude certain types
        for exclude_word in self.chat_filters["exclude_keywords"]:
            if exclude_word in chat_name:
                return False
        
        # Check for community indicators
        community_score = 0
        for keyword in self.chat_filters["community_keywords"]:
            if keyword in chat_name:
                community_score += 1
        
        # Check for business indicators
        business_score = 0
        for keyword in self.chat_filters["business_keywords"]:
            if keyword in chat_name:
                business_score += 2  # Business keywords are more valuable
        
        # High-value if it has community or business indicators
        return (community_score > 0) or (business_score > 0)
    
    def calculate_chat_priority(self, chat: Dict[str, Any]) -> int:
        """Calculate priority score for chat"""
        chat_name = chat.get("name", "").lower()
        score = 0
        
        # Business keywords get highest priority
        for keyword in self.chat_filters["business_keywords"]:
            if keyword in chat_name:
                score += 10
        
        # Community keywords get medium priority
        for keyword in self.chat_filters["community_keywords"]:
            if keyword in chat_name:
                score += 5
        
        # Group chats generally have more activity
        if "group" in chat_name or "_g.us" in chat.get("jid", ""):
            score += 3
        
        return score
    
    async def discover_high_value_chats(self, max_chats: int = 100) -> List[Dict[str, Any]]:
        """Discover and rank high-value chats"""
        print(f"🔍 Discovering high-value chats from {max_chats} available chats...")
        
        all_chats = []
        page = 0
        limit = 20
        
        while len(all_chats) < max_chats:
            try:
                result = await self.client.call_tool("list_chats", {
                    "limit": min(limit, max_chats - len(all_chats)),
                    "page": page,
                    "include_last_message": True,
                    "sort_by": "last_active"
                })
                
                parsed_result = self.parse_mcp_response(result)
                if parsed_result is None:
                    break
                
                chats = self.parse_chat_data(parsed_result) if isinstance(parsed_result, list) else []
                
                if not chats:
                    break
                
                all_chats.extend(chats)
                page += 1
                
                if len(chats) < limit:
                    break
                    
            except Exception as e:
                print(f"❌ Error discovering chats: {e}")
                break
        
        # Filter and rank high-value chats
        high_value_chats = []
        for chat in all_chats:
            if self.is_high_value_chat(chat):
                chat["priority_score"] = self.calculate_chat_priority(chat)
                high_value_chats.append(chat)
        
        # Sort by priority score (highest first)
        high_value_chats.sort(key=lambda x: x["priority_score"], reverse=True)
        
        print(f"✅ Found {len(high_value_chats)} high-value chats out of {len(all_chats)} total")
        
        # Show top candidates
        print(f"\n🎯 TOP HIGH-VALUE CHATS:")
        for i, chat in enumerate(high_value_chats[:10]):
            print(f"  {i+1}. {chat.get('name', 'Unknown')} (Score: {chat['priority_score']})")
        
        return high_value_chats
    
    async def extract_targeted_chat(self, chat: Dict[str, Any], max_messages: int = 1000) -> Dict[str, Any]:
        """Extract deep data from a specific targeted chat"""
        chat_name = chat.get("name", "Unknown")
        chat_jid = chat.get("jid", "")
        
        print(f"  📱 Extracting: {chat_name}")
        print(f"    Priority Score: {chat.get('priority_score', 0)}")
        
        try:
            # Extract deep message history
            all_messages = []
            page = 0
            limit = 50
            
            while len(all_messages) < max_messages:
                try:
                    result = await self.client.call_tool("list_messages", {
                        "chat_jid": chat_jid,
                        "limit": min(limit, max_messages - len(all_messages)),
                        "page": page,
                        "include_context": True,
                        "context_before": 2,
                        "context_after": 2
                    })
                    
                    parsed_result = self.parse_mcp_response(result)
                    if parsed_result is None:
                        break
                    
                    messages = parsed_result if isinstance(parsed_result, list) else []
                    
                    if not messages:
                        break
                    
                    all_messages.extend(messages)
                    print(f"    📜 Page {page + 1}: {len(messages)} messages (total: {len(all_messages)})")
                    
                    # Rate limiting
                    await asyncio.sleep(self.message_delay)
                    page += 1
                    
                    if len(messages) < limit:
                        break
                        
                except Exception as e:
                    print(f"    ❌ Error on page {page}: {e}")
                    break
            
            # Enhanced chat data
            enhanced_chat = {
                **chat,
                "messages": all_messages,
                "message_count": len(all_messages),
                "extraction_time": datetime.now().isoformat(),
                "extraction_type": "targeted"
            }
            
            # Save individual chat file
            chat_filename = f"targeted_chat_{chat_jid.replace('@', '_').replace('-', '_')}.json"
            self.save_json(enhanced_chat, chat_filename)
            
            print(f"    ✅ Extracted {len(all_messages)} messages")
            return enhanced_chat
            
        except Exception as e:
            print(f"    ❌ Error extracting chat: {e}")
            return chat
    
    def save_json(self, data: Any, filename: str) -> str:
        """Save data to JSON file"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath
    
    def analyze_targeted_data(self, targeted_chats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze targeted chat data for concentrated business opportunities"""
        print("🔍 Analyzing targeted chat data for concentrated opportunities...")
        
        from whatsapp_mcp_extractor import identify_monetization_keywords
        
        analysis = {
            "extraction_time": datetime.now().isoformat(),
            "extraction_type": "targeted",
            "total_targeted_chats": len(targeted_chats),
            "total_messages": sum(len(chat.get("messages", [])) for chat in targeted_chats),
            "chat_analysis": [],
            "concentrated_opportunities": {
                "product_opportunities": {},
                "service_needs": {},
                "marketing_insights": {}
            },
            "high_concentration_chats": [],
            "business_intelligence": {
                "community_insights": {},
                "professional_networks": {},
                "market_segments": {}
            }
        }
        
        # Analyze each targeted chat
        for chat in targeted_chats:
            chat_name = chat.get("name", "Unknown")
            chat_jid = chat.get("jid", "")
            messages = chat.get("messages", [])
            priority_score = chat.get("priority_score", 0)
            
            chat_analysis = {
                "chat_name": chat_name,
                "chat_jid": chat_jid,
                "priority_score": priority_score,
                "message_count": len(messages),
                "opportunity_density": 0,
                "keyword_concentrations": {},
                "business_themes": []
            }
            
            # Analyze all messages in this chat
            chat_opportunities = {"products": [], "services": [], "marketing": []}
            
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
                    
                    # Count keywords by category
                    for category in ["products", "services", "marketing"]:
                        for keyword in keywords[category]:
                            if category == "products":
                                key = "product_opportunities"
                            elif category == "services":
                                key = "service_needs"
                            else:
                                key = "marketing_insights"
                            
                            # Global count
                            if keyword not in analysis["concentrated_opportunities"][key]:
                                analysis["concentrated_opportunities"][key][keyword] = 0
                            analysis["concentrated_opportunities"][key][keyword] += 1
                            
                            # Chat-specific count
                            if keyword not in chat_analysis["keyword_concentrations"]:
                                chat_analysis["keyword_concentrations"][keyword] = 0
                            chat_analysis["keyword_concentrations"][keyword] += 1
                            
                            chat_opportunities[category].append(keyword)
            
            # Calculate opportunity density (opportunities per message)
            total_opportunities = sum(len(v) for v in chat_opportunities.values())
            chat_analysis["opportunity_density"] = total_opportunities / max(len(messages), 1)
            
            # Identify business themes
            if chat_analysis["keyword_concentrations"]:
                top_keywords = sorted(chat_analysis["keyword_concentrations"].items(), 
                                    key=lambda x: x[1], reverse=True)[:5]
                chat_analysis["business_themes"] = [kw for kw, count in top_keywords]
            
            analysis["chat_analysis"].append(chat_analysis)
            
            # Mark high-concentration chats
            if chat_analysis["opportunity_density"] > 0.1:  # More than 10% of messages have opportunities
                analysis["high_concentration_chats"].append({
                    "chat_name": chat_name,
                    "opportunity_density": chat_analysis["opportunity_density"],
                    "total_opportunities": total_opportunities,
                    "top_themes": chat_analysis["business_themes"][:3]
                })
        
        return analysis
    
    async def run_targeted_extraction(self, target_chat_names: Optional[List[str]] = None, 
                                    max_discovery_chats: int = 100, 
                                    max_target_chats: int = 10,
                                    max_messages_per_chat: int = 1000):
        """Run targeted extraction on specific high-value chats"""
        print("🎯 TARGETED WhatsApp Chat Extraction")
        print("=" * 60)
        
        session_start = datetime.now()
        
        try:
            # Connect
            if not await self.connect():
                return False
            
            # Discover or use specified target chats
            if target_chat_names:
                print(f"🎯 Targeting specific chats: {', '.join(target_chat_names)}")
                # TODO: Implement specific chat name targeting
                target_chats = []
            else:
                print(f"🔍 Auto-discovering high-value chats...")
                discovered_chats = await self.discover_high_value_chats(max_discovery_chats)
                target_chats = discovered_chats[:max_target_chats]
            
            if not target_chats:
                print("❌ No target chats found")
                return False
            
            print(f"\n🎯 Extracting from {len(target_chats)} targeted chats:")
            for i, chat in enumerate(target_chats):
                print(f"  {i+1}. {chat.get('name', 'Unknown')} (Score: {chat.get('priority_score', 0)})")
            
            # Extract from each targeted chat
            extracted_chats = []
            for i, chat in enumerate(target_chats):
                print(f"\n🔄 Processing chat {i+1}/{len(target_chats)}:")
                
                extracted_chat = await self.extract_targeted_chat(chat, max_messages_per_chat)
                extracted_chats.append(extracted_chat)
                
                # Rate limiting between chats
                if i < len(target_chats) - 1:
                    await asyncio.sleep(self.chat_delay)
            
            # Analyze concentrated data
            analysis = self.analyze_targeted_data(extracted_chats)
            
            # Save results
            complete_data = {
                "extraction_metadata": {
                    "session_start": session_start.isoformat(),
                    "session_end": datetime.now().isoformat(),
                    "extraction_type": "targeted",
                    "target_chats": len(extracted_chats),
                    "total_messages": analysis["total_messages"],
                    "extraction_duration_minutes": (datetime.now() - session_start).total_seconds() / 60
                },
                "targeted_chats": extracted_chats
            }
            
            self.save_json(complete_data, "targeted_whatsapp_complete.json")
            self.save_json(analysis, "targeted_monetization_analysis.json")
            
            # Print results
            self.print_targeted_results(analysis, session_start)
            
            return True
            
        except Exception as e:
            print(f"❌ Targeted extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            if self.client:
                await self.client.close()
    
    def print_targeted_results(self, analysis: Dict[str, Any], session_start: datetime):
        """Print targeted extraction results"""
        duration = datetime.now() - session_start
        
        print("\n" + "=" * 60)
        print("🎉 TARGETED EXTRACTION COMPLETED!")
        print("=" * 60)
        
        print(f"⏱️  Duration: {duration.total_seconds() / 60:.1f} minutes")
        print(f"🎯 Targeted chats: {analysis['total_targeted_chats']}")
        print(f"💬 Messages analyzed: {analysis['total_messages']}")
        print(f"🔥 High-concentration chats: {len(analysis['high_concentration_chats'])}")
        
        # Show high-concentration chats
        if analysis['high_concentration_chats']:
            print(f"\n🔥 HIGH-CONCENTRATION OPPORTUNITY CHATS:")
            for chat in analysis['high_concentration_chats']:
                print(f"  • {chat['chat_name']}")
                print(f"    Density: {chat['opportunity_density']:.2f} opportunities/message")
                print(f"    Themes: {', '.join(chat['top_themes'])}")
        
        # Show concentrated opportunities
        print(f"\n🎯 CONCENTRATED OPPORTUNITIES:")
        
        for category, keywords in analysis["concentrated_opportunities"].items():
            if keywords:
                print(f"\n{category.replace('_', ' ').title()}:")
                sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
                for keyword, count in sorted_keywords[:5]:
                    print(f"  • '{keyword}': {count} mentions")
        
        print(f"\n💾 Data saved to: {os.path.abspath(self.output_dir)}")
        print("📁 Targeted extraction files:")
        print("  • targeted_whatsapp_complete.json - Complete targeted dataset")
        print("  • targeted_monetization_analysis.json - Concentrated business analysis")
        print("  • targeted_chat_*.json - Individual high-value chat files")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Targeted WhatsApp chat extraction")
    parser.add_argument("--target-chats", nargs="+", help="Specific chat names to target")
    parser.add_argument("--max-discovery", type=int, default=100, help="Max chats to scan for discovery")
    parser.add_argument("--max-targets", type=int, default=10, help="Max high-value chats to extract")
    parser.add_argument("--max-messages", type=int, default=1000, help="Max messages per targeted chat")
    
    args = parser.parse_args()
    
    extractor = TargetedExtractor()
    
    try:
        success = await extractor.run_targeted_extraction(
            target_chat_names=args.target_chats,
            max_discovery_chats=args.max_discovery,
            max_target_chats=args.max_targets,
            max_messages_per_chat=args.max_messages
        )
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️ Extraction interrupted")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))