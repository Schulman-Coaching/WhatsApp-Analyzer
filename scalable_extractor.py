#!/usr/bin/env python3
"""
Scalable WhatsApp Data Extractor

This script provides enhanced extraction capabilities with:
- Increased chat processing limits
- Deeper message history extraction
- Progress tracking and resumption
- Batch processing with rate limiting
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import time

from mcp_stdio_client import MCPStdioClient


class ScalableExtractor:
    """Scalable WhatsApp data extractor for large-scale analysis"""
    
    def __init__(self):
        self.client = None
        self.output_dir = "scalable_extracted_data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.server_path = r"C:\Users\elie\OneDrive\Documents\Cline\MCP\whatsapp-mcp\whatsapp-mcp-server\main.py"
        
        # Progress tracking
        self.progress_file = os.path.join(self.output_dir, "extraction_progress.json")
        self.progress = self.load_progress()
        
        # Rate limiting settings
        self.chat_delay = 2.0  # Seconds between chat processing
        self.message_delay = 1.0  # Seconds between message requests
        self.batch_size = 10  # Chats per batch
        
    def load_progress(self) -> Dict[str, Any]:
        """Load extraction progress from file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "last_extraction": None,
            "processed_chats": [],
            "failed_chats": [],
            "total_messages_extracted": 0,
            "extraction_sessions": []
        }
    
    def save_progress(self):
        """Save extraction progress"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
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
    
    async def extract_all_chats(self, max_chats: int = 50) -> List[Dict[str, Any]]:
        """Extract all chats with pagination"""
        all_chats = []
        page = 0
        limit = 20  # Smaller batches for reliability
        
        print(f"📱 Extracting up to {max_chats} chats...")
        
        while len(all_chats) < max_chats:
            try:
                print(f"  Fetching page {page + 1} (chats {len(all_chats) + 1}-{min(len(all_chats) + limit, max_chats)})...")
                
                result = await self.client.call_tool("list_chats", {
                    "limit": min(limit, max_chats - len(all_chats)),
                    "page": page,
                    "include_last_message": True,
                    "sort_by": "last_active"
                })
                
                parsed_result = self.parse_mcp_response(result)
                if parsed_result is None:
                    break
                
                if isinstance(parsed_result, list):
                    chats = self.parse_chat_data(parsed_result)
                else:
                    break
                
                if not chats:
                    print("  No more chats found")
                    break
                
                all_chats.extend(chats)
                print(f"  ✅ Found {len(chats)} chats (total: {len(all_chats)})")
                
                # Rate limiting
                await asyncio.sleep(1)
                page += 1
                
                # If we got fewer chats than requested, we've reached the end
                if len(chats) < limit:
                    break
                    
            except Exception as e:
                print(f"❌ Error on page {page}: {e}")
                break
        
        print(f"✅ Total chats extracted: {len(all_chats)}")
        return all_chats
    
    async def extract_deep_message_history(self, chat_jid: str, max_messages: int = 200) -> List[Dict[str, Any]]:
        """Extract deep message history with pagination"""
        all_messages = []
        page = 0
        limit = 50  # Messages per page
        
        print(f"    📜 Extracting up to {max_messages} messages...")
        
        while len(all_messages) < max_messages:
            try:
                result = await self.client.call_tool("list_messages", {
                    "chat_jid": chat_jid,
                    "limit": min(limit, max_messages - len(all_messages)),
                    "page": page,
                    "include_context": True,
                    "context_before": 1,
                    "context_after": 1
                })
                
                parsed_result = self.parse_mcp_response(result)
                if parsed_result is None:
                    break
                
                messages = parsed_result if isinstance(parsed_result, list) else []
                
                if not messages:
                    break
                
                all_messages.extend(messages)
                print(f"      Page {page + 1}: {len(messages)} messages (total: {len(all_messages)})")
                
                # Rate limiting
                await asyncio.sleep(self.message_delay)
                page += 1
                
                if len(messages) < limit:
                    break
                    
            except Exception as e:
                print(f"❌ Error extracting messages page {page}: {e}")
                break
        
        return all_messages
    
    async def process_chat_batch(self, chats: List[Dict[str, Any]], batch_num: int, max_messages_per_chat: int = 200) -> List[Dict[str, Any]]:
        """Process a batch of chats with deep message extraction"""
        print(f"\n🔄 Processing batch {batch_num} ({len(chats)} chats)...")
        
        processed_chats = []
        
        for i, chat in enumerate(chats):
            chat_name = chat.get("name", "Unknown")
            chat_jid = chat.get("jid", "")
            
            print(f"  📱 {i+1}/{len(chats)}: {chat_name}")
            
            # Skip if already processed
            if chat_jid in self.progress["processed_chats"]:
                print(f"    ⏭️ Already processed, skipping...")
                continue
            
            try:
                # Extract deep message history
                if chat_jid:
                    messages = await self.extract_deep_message_history(chat_jid, max_messages_per_chat)
                    chat["messages"] = messages
                    chat["message_count"] = len(messages)
                    
                    self.progress["total_messages_extracted"] += len(messages)
                    
                    # Save individual chat data
                    chat_filename = f"chat_{chat_jid.replace('@', '_').replace('-', '_')}.json"
                    self.save_json(chat, chat_filename)
                    
                    # Mark as processed
                    self.progress["processed_chats"].append(chat_jid)
                    self.save_progress()
                
                processed_chats.append(chat)
                
                # Rate limiting between chats
                if i < len(chats) - 1:
                    await asyncio.sleep(self.chat_delay)
                    
            except Exception as e:
                print(f"❌ Error processing chat {chat_name}: {e}")
                self.progress["failed_chats"].append({
                    "chat_jid": chat_jid,
                    "chat_name": chat_name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                self.save_progress()
        
        return processed_chats
    
    def save_json(self, data: Any, filename: str) -> str:
        """Save data to JSON file"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath
    
    def analyze_scalable_data(self, all_chats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze large-scale data for monetization opportunities"""
        print("🔍 Analyzing large-scale data for monetization opportunities...")
        
        from whatsapp_mcp_extractor import identify_monetization_keywords
        
        analysis = {
            "extraction_time": datetime.now().isoformat(),
            "total_chats": len(all_chats),
            "total_messages": sum(len(chat.get("messages", [])) for chat in all_chats),
            "monetization_keywords": {
                "product_opportunities": {},
                "service_needs": {},
                "marketing_insights": {}
            },
            "high_value_chats": [],
            "opportunity_trends": {},
            "geographic_insights": {},
            "temporal_patterns": {}
        }
        
        # Process each chat
        for chat in all_chats:
            chat_name = chat.get("name", "Unknown")
            chat_jid = chat.get("jid", "")
            messages = chat.get("messages", [])
            last_message = chat.get("last_message", "")
            
            chat_indicators = 0
            chat_opportunities = []
            
            # Analyze all messages
            all_texts = [last_message] if last_message else []
            for message in messages:
                text = ""
                if isinstance(message, dict):
                    text = (message.get("text") or 
                           message.get("content") or 
                           message.get("body") or "")
                elif isinstance(message, str):
                    text = message
                
                if text:
                    all_texts.append(text)
            
            # Analyze all text content
            for text in all_texts:
                if text:
                    keywords = identify_monetization_keywords(text)
                    
                    if any(keywords.values()):
                        chat_indicators += 1
                        
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
                        
                        # Store opportunity
                        chat_opportunities.append({
                            "text": text[:100] + "..." if len(text) > 100 else text,
                            "keywords": keywords
                        })
            
            # Mark high-value chats
            if chat_indicators >= 3:
                analysis["high_value_chats"].append({
                    "chat_name": chat_name,
                    "chat_jid": chat_jid,
                    "message_count": len(messages),
                    "monetization_indicators": chat_indicators,
                    "opportunity_sample": chat_opportunities[:3]
                })
        
        # Calculate trends and patterns
        analysis["opportunity_trends"] = self.calculate_trends(analysis["monetization_keywords"])
        
        return analysis
    
    def calculate_trends(self, keywords: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
        """Calculate opportunity trends from keyword data"""
        trends = {
            "top_product_opportunities": [],
            "top_service_needs": [],
            "emerging_keywords": [],
            "market_gaps": []
        }
        
        # Top opportunities by frequency
        for category, keyword_counts in keywords.items():
            if keyword_counts:
                sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
                
                if category == "product_opportunities":
                    trends["top_product_opportunities"] = sorted_keywords[:10]
                elif category == "service_needs":
                    trends["top_service_needs"] = sorted_keywords[:10]
        
        return trends
    
    async def run_scalable_extraction(self, max_chats: int = 50, max_messages_per_chat: int = 200):
        """Run large-scale extraction with progress tracking"""
        print("🎯 SCALABLE WhatsApp Data Extraction")
        print("=" * 60)
        print(f"Target: {max_chats} chats, {max_messages_per_chat} messages per chat")
        print(f"Estimated total messages: {max_chats * max_messages_per_chat}")
        print("=" * 60)
        
        session_start = datetime.now()
        
        try:
            # Connect
            if not await self.connect():
                return False
            
            # Extract all chats
            all_chats = await self.extract_all_chats(max_chats)
            if not all_chats:
                return False
            
            # Process in batches
            total_processed = 0
            all_processed_chats = []
            
            for i in range(0, len(all_chats), self.batch_size):
                batch = all_chats[i:i + self.batch_size]
                batch_num = (i // self.batch_size) + 1
                
                processed_batch = await self.process_chat_batch(batch, batch_num, max_messages_per_chat)
                all_processed_chats.extend(processed_batch)
                total_processed += len(processed_batch)
                
                print(f"\n📊 Progress: {total_processed}/{len(all_chats)} chats processed")
                
                # Save incremental results
                if batch_num % 3 == 0:  # Every 3 batches
                    self.save_json(all_processed_chats, f"incremental_results_batch_{batch_num}.json")
            
            # Final analysis
            analysis = self.analyze_scalable_data(all_processed_chats)
            
            # Save complete results
            complete_data = {
                "extraction_metadata": {
                    "session_start": session_start.isoformat(),
                    "session_end": datetime.now().isoformat(),
                    "total_chats": len(all_processed_chats),
                    "total_messages": analysis["total_messages"],
                    "extraction_duration_minutes": (datetime.now() - session_start).total_seconds() / 60,
                    "extractor_version": "scalable_v1.0"
                },
                "chats": all_processed_chats
            }
            
            self.save_json(complete_data, "scalable_whatsapp_complete.json")
            self.save_json(analysis, "scalable_monetization_analysis.json")
            
            # Update progress
            self.progress["extraction_sessions"].append({
                "session_start": session_start.isoformat(),
                "session_end": datetime.now().isoformat(),
                "chats_processed": len(all_processed_chats),
                "messages_extracted": analysis["total_messages"]
            })
            self.save_progress()
            
            # Print results
            self.print_scalable_results(analysis, session_start)
            
            return True
            
        except Exception as e:
            print(f"❌ Scalable extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            if self.client:
                await self.client.close()
    
    def print_scalable_results(self, analysis: Dict[str, Any], session_start: datetime):
        """Print scalable extraction results"""
        duration = datetime.now() - session_start
        
        print("\n" + "=" * 60)
        print("🎉 SCALABLE EXTRACTION COMPLETED!")
        print("=" * 60)
        
        print(f"⏱️  Duration: {duration.total_seconds() / 60:.1f} minutes")
        print(f"📊 Chats processed: {analysis['total_chats']}")
        print(f"💬 Messages analyzed: {analysis['total_messages']}")
        print(f"🎯 High-value chats: {len(analysis['high_value_chats'])}")
        print(f"📈 Processing rate: {analysis['total_messages'] / (duration.total_seconds() / 60):.1f} messages/minute")
        
        # Show top opportunities
        print("\n🔍 TOP MONETIZATION OPPORTUNITIES:")
        
        for category, keywords in analysis["monetization_keywords"].items():
            if keywords:
                print(f"\n{category.replace('_', ' ').title()}:")
                sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
                for keyword, count in sorted_keywords[:5]:
                    print(f"  • '{keyword}': {count} mentions")
        
        # Show trends
        trends = analysis.get("opportunity_trends", {})
        if trends.get("top_product_opportunities"):
            print(f"\n📈 TOP PRODUCT TRENDS:")
            for keyword, count in trends["top_product_opportunities"][:3]:
                print(f"  • {keyword}: {count} mentions")
        
        print(f"\n💾 Data saved to: {os.path.abspath(self.output_dir)}")
        print("📁 Scalable extraction files:")
        print("  • scalable_whatsapp_complete.json - Complete dataset")
        print("  • scalable_monetization_analysis.json - Business analysis")
        print("  • extraction_progress.json - Progress tracking")
        print("  • chat_*.json - Individual chat files")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scalable WhatsApp data extraction")
    parser.add_argument("--max-chats", type=int, default=50, help="Maximum chats to process")
    parser.add_argument("--max-messages", type=int, default=200, help="Maximum messages per chat")
    parser.add_argument("--resume", action="store_true", help="Resume from previous extraction")
    
    args = parser.parse_args()
    
    extractor = ScalableExtractor()
    
    if args.resume:
        print("📂 Resuming from previous extraction...")
        print(f"Previously processed: {len(extractor.progress['processed_chats'])} chats")
        print(f"Total messages extracted: {extractor.progress['total_messages_extracted']}")
    
    try:
        success = await extractor.run_scalable_extraction(args.max_chats, args.max_messages)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️ Extraction interrupted - progress saved")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))