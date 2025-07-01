#!/usr/bin/env python3
"""
Real-time WhatsApp Opportunity Monitor

This script provides continuous monitoring capabilities with:
- Real-time message monitoring
- Automatic opportunity detection
- Alert system for high-value opportunities
- Dashboard for live insights
- Configurable monitoring intervals
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
import time
import threading
from collections import defaultdict, deque

from mcp_stdio_client import MCPStdioClient


class RealTimeMonitor:
    """Real-time WhatsApp opportunity monitoring system"""
    
    def __init__(self):
        self.client = None
        self.monitoring = False
        self.output_dir = "realtime_monitoring"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.server_path = r"C:\Users\elie\OneDrive\Documents\Cline\MCP\whatsapp-mcp\whatsapp-mcp-server\main.py"
        
        # Monitoring configuration
        self.monitor_interval = 30  # seconds between checks
        self.opportunity_threshold = 2  # minimum keywords for alert
        self.max_history_size = 1000  # messages to keep in memory
        
        # State tracking
        self.seen_messages: Set[str] = set()
        self.message_history = deque(maxlen=self.max_history_size)
        self.opportunity_alerts = []
        self.chat_activity = defaultdict(list)
        self.keyword_trends = defaultdict(int)
        
        # Alert configuration
        self.high_value_keywords = {
            "urgent": ["urgent", "asap", "immediately", "emergency"],
            "business": ["business", "startup", "investment", "funding", "revenue"],
            "services": ["hire", "looking for", "need help", "recommend", "service"],
            "products": ["buy", "sell", "purchase", "product", "deal", "discount"],
            "networking": ["connect", "introduce", "meeting", "collaboration", "partner"]
        }
        
        # Statistics
        self.stats = {
            "monitoring_start": None,
            "total_messages_processed": 0,
            "opportunities_detected": 0,
            "alerts_sent": 0,
            "active_chats": set(),
            "peak_activity_hour": None
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
            print("🚀 Connecting to WhatsApp MCP server for real-time monitoring...")
            
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
    
    def detect_opportunities(self, text: str) -> Dict[str, List[str]]:
        """Detect monetization opportunities in text"""
        opportunities = {
            "urgent": [],
            "business": [],
            "services": [],
            "products": [],
            "networking": []
        }
        
        text_lower = text.lower()
        
        for category, keywords in self.high_value_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    opportunities[category].append(keyword)
                    self.keyword_trends[keyword] += 1
        
        return opportunities
    
    def calculate_opportunity_score(self, opportunities: Dict[str, List[str]]) -> int:
        """Calculate opportunity score based on detected keywords"""
        score = 0
        weights = {
            "urgent": 3,
            "business": 2,
            "services": 2,
            "products": 1,
            "networking": 1
        }
        
        for category, keywords in opportunities.items():
            score += len(keywords) * weights.get(category, 1)
        
        return score
    
    def should_alert(self, opportunity_score: int, opportunities: Dict[str, List[str]]) -> bool:
        """Determine if an opportunity warrants an alert"""
        # High-value keywords trigger immediate alerts
        if opportunities["urgent"] or opportunities["business"]:
            return True
        
        # Multiple service/product keywords
        if opportunity_score >= self.opportunity_threshold:
            return True
        
        return False
    
    def create_alert(self, chat_name: str, chat_jid: str, message: Dict[str, Any], 
                    opportunities: Dict[str, List[str]], score: int) -> Dict[str, Any]:
        """Create an opportunity alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "alert_id": f"alert_{len(self.opportunity_alerts) + 1}",
            "chat_name": chat_name,
            "chat_jid": chat_jid,
            "opportunity_score": score,
            "opportunities": opportunities,
            "message_preview": message.get("text", "")[:200],
            "sender": message.get("sender", "Unknown"),
            "urgency": "HIGH" if opportunities["urgent"] or score >= 5 else "MEDIUM"
        }
        
        self.opportunity_alerts.append(alert)
        self.stats["alerts_sent"] += 1
        
        return alert
    
    async def monitor_recent_messages(self) -> List[Dict[str, Any]]:
        """Monitor recent messages across all chats"""
        try:
            # Get active chats
            result = await self.client.call_tool("list_chats", {
                "limit": 20,
                "include_last_message": True,
                "sort_by": "last_active"
            })
            
            parsed_result = self.parse_mcp_response(result)
            if parsed_result is None:
                return []
            
            chats = self.parse_chat_data(parsed_result) if isinstance(parsed_result, list) else []
            new_opportunities = []
            
            for chat in chats:
                chat_name = chat.get("name", "Unknown")
                chat_jid = chat.get("jid", "")
                
                if not chat_jid:
                    continue
                
                self.stats["active_chats"].add(chat_jid)
                
                # Get recent messages from this chat
                try:
                    messages_result = await self.client.call_tool("list_messages", {
                        "chat_jid": chat_jid,
                        "limit": 5,  # Only recent messages
                        "page": 0
                    })
                    
                    messages_parsed = self.parse_mcp_response(messages_result)
                    messages = messages_parsed if isinstance(messages_parsed, list) else []
                    
                    for message in messages:
                        message_id = f"{chat_jid}_{message.get('id', '')}"
                        
                        # Skip if we've already processed this message
                        if message_id in self.seen_messages:
                            continue
                        
                        self.seen_messages.add(message_id)
                        self.message_history.append({
                            "chat_name": chat_name,
                            "chat_jid": chat_jid,
                            "message": message,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        text = message.get("text", "") or message.get("content", "") or message.get("body", "")
                        
                        if text:
                            self.stats["total_messages_processed"] += 1
                            
                            # Detect opportunities
                            opportunities = self.detect_opportunities(text)
                            opportunity_score = self.calculate_opportunity_score(opportunities)
                            
                            if opportunity_score > 0:
                                self.stats["opportunities_detected"] += 1
                                
                                # Track chat activity
                                self.chat_activity[chat_jid].append({
                                    "timestamp": datetime.now().isoformat(),
                                    "score": opportunity_score,
                                    "opportunities": opportunities
                                })
                                
                                # Create alert if warranted
                                if self.should_alert(opportunity_score, opportunities):
                                    alert = self.create_alert(chat_name, chat_jid, message, opportunities, opportunity_score)
                                    new_opportunities.append(alert)
                                    
                                    print(f"🚨 OPPORTUNITY ALERT: {chat_name}")
                                    print(f"   Score: {opportunity_score}")
                                    print(f"   Keywords: {sum(len(v) for v in opportunities.values())}")
                                    print(f"   Preview: {text[:100]}...")
                    
                    await asyncio.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    print(f"⚠️ Error monitoring chat {chat_name}: {e}")
            
            return new_opportunities
            
        except Exception as e:
            print(f"❌ Error monitoring messages: {e}")
            return []
    
    def save_monitoring_data(self):
        """Save current monitoring state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save alerts
        alerts_file = os.path.join(self.output_dir, f"alerts_{timestamp}.json")
        with open(alerts_file, 'w', encoding='utf-8') as f:
            json.dump(self.opportunity_alerts, f, ensure_ascii=False, indent=2)
        
        # Save statistics
        stats_data = {
            **self.stats,
            "active_chats": list(self.stats["active_chats"]),
            "keyword_trends": dict(self.keyword_trends),
            "chat_activity_summary": {
                chat_jid: len(activities) 
                for chat_jid, activities in self.chat_activity.items()
            }
        }
        
        stats_file = os.path.join(self.output_dir, f"monitoring_stats_{timestamp}.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
        
        # Save recent message history
        history_file = os.path.join(self.output_dir, f"message_history_{timestamp}.json")
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.message_history), f, ensure_ascii=False, indent=2)
    
    def print_monitoring_dashboard(self):
        """Print real-time monitoring dashboard"""
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
        
        print("🔴 REAL-TIME WhatsApp OPPORTUNITY MONITOR")
        print("=" * 60)
        
        if self.stats["monitoring_start"]:
            duration = datetime.now() - datetime.fromisoformat(self.stats["monitoring_start"])
            print(f"⏱️  Monitoring Duration: {duration.total_seconds() / 60:.1f} minutes")
        
        print(f"📊 Messages Processed: {self.stats['total_messages_processed']}")
        print(f"🎯 Opportunities Detected: {self.stats['opportunities_detected']}")
        print(f"🚨 Alerts Sent: {self.stats['alerts_sent']}")
        print(f"💬 Active Chats: {len(self.stats['active_chats'])}")
        
        # Recent alerts
        if self.opportunity_alerts:
            print(f"\n🚨 RECENT ALERTS ({len(self.opportunity_alerts)}):")
            for alert in self.opportunity_alerts[-5:]:  # Last 5 alerts
                urgency_icon = "🔥" if alert["urgency"] == "HIGH" else "⚡"
                print(f"  {urgency_icon} {alert['chat_name']} (Score: {alert['opportunity_score']})")
                print(f"     {alert['message_preview'][:80]}...")
        
        # Top trending keywords
        if self.keyword_trends:
            print(f"\n📈 TRENDING KEYWORDS:")
            sorted_keywords = sorted(self.keyword_trends.items(), key=lambda x: x[1], reverse=True)
            for keyword, count in sorted_keywords[:5]:
                print(f"  • '{keyword}': {count} mentions")
        
        print(f"\n🔄 Next check in {self.monitor_interval} seconds...")
        print("Press Ctrl+C to stop monitoring")
    
    async def start_monitoring(self, duration_minutes: Optional[int] = None):
        """Start real-time monitoring"""
        print("🎯 STARTING REAL-TIME MONITORING")
        print("=" * 60)
        
        self.monitoring = True
        self.stats["monitoring_start"] = datetime.now().isoformat()
        
        try:
            # Connect
            if not await self.connect():
                return False
            
            end_time = None
            if duration_minutes:
                end_time = datetime.now() + timedelta(minutes=duration_minutes)
                print(f"⏰ Monitoring for {duration_minutes} minutes")
            else:
                print("⏰ Monitoring indefinitely (Ctrl+C to stop)")
            
            cycle_count = 0
            
            while self.monitoring:
                cycle_count += 1
                cycle_start = datetime.now()
                
                print(f"\n🔄 Monitoring cycle {cycle_count} - {cycle_start.strftime('%H:%M:%S')}")
                
                # Monitor recent messages
                new_opportunities = await self.monitor_recent_messages()
                
                if new_opportunities:
                    print(f"✨ Found {len(new_opportunities)} new opportunities this cycle")
                
                # Save data periodically
                if cycle_count % 10 == 0:  # Every 10 cycles
                    self.save_monitoring_data()
                    print("💾 Monitoring data saved")
                
                # Print dashboard
                self.print_monitoring_dashboard()
                
                # Check if we should stop
                if end_time and datetime.now() >= end_time:
                    print(f"\n⏰ Monitoring duration completed")
                    break
                
                # Wait for next cycle
                await asyncio.sleep(self.monitor_interval)
            
            return True
            
        except KeyboardInterrupt:
            print(f"\n⏹️ Monitoring stopped by user")
            return True
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.monitoring = False
            if self.client:
                await self.client.close()
            
            # Final save
            self.save_monitoring_data()
            self.print_final_summary()
    
    def print_final_summary(self):
        """Print final monitoring summary"""
        print("\n" + "=" * 60)
        print("🏁 MONITORING SESSION COMPLETED")
        print("=" * 60)
        
        if self.stats["monitoring_start"]:
            duration = datetime.now() - datetime.fromisoformat(self.stats["monitoring_start"])
            print(f"⏱️  Total Duration: {duration.total_seconds() / 60:.1f} minutes")
        
        print(f"📊 Total Messages: {self.stats['total_messages_processed']}")
        print(f"🎯 Opportunities: {self.stats['opportunities_detected']}")
        print(f"🚨 Alerts Generated: {self.stats['alerts_sent']}")
        print(f"💬 Chats Monitored: {len(self.stats['active_chats'])}")
        
        if self.stats['total_messages_processed'] > 0:
            opportunity_rate = (self.stats['opportunities_detected'] / self.stats['total_messages_processed']) * 100
            print(f"📈 Opportunity Rate: {opportunity_rate:.1f}%")
        
        # Top opportunities
        if self.opportunity_alerts:
            high_value_alerts = [a for a in self.opportunity_alerts if a["urgency"] == "HIGH"]
            print(f"\n🔥 High-Value Alerts: {len(high_value_alerts)}")
            
            for alert in high_value_alerts[-3:]:  # Last 3 high-value
                print(f"  • {alert['chat_name']}: {alert['message_preview'][:60]}...")
        
        print(f"\n💾 Data saved to: {os.path.abspath(self.output_dir)}")
        print("📁 Monitoring files:")
        print("  • alerts_*.json - Opportunity alerts")
        print("  • monitoring_stats_*.json - Session statistics")
        print("  • message_history_*.json - Message history")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-time WhatsApp opportunity monitoring")
    parser.add_argument("--duration", type=int, help="Monitoring duration in minutes (default: indefinite)")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds (default: 30)")
    parser.add_argument("--threshold", type=int, default=2, help="Opportunity threshold for alerts (default: 2)")
    
    args = parser.parse_args()
    
    monitor = RealTimeMonitor()
    monitor.monitor_interval = args.interval
    monitor.opportunity_threshold = args.threshold
    
    try:
        success = await monitor.start_monitoring(args.duration)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring interrupted")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))