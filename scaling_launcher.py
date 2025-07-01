#!/usr/bin/env python3
"""
Unified Scaling Launcher

This script provides a unified interface for all scaling operations:
- Large-scale data extraction
- Real-time monitoring
- Configuration management
- Performance optimization
- Resource monitoring
"""

import asyncio
import sys
import os
import argparse
from datetime import datetime
from typing import Optional

from scaling_config import ScalingConfigManager
from scalable_extractor import ScalableExtractor
from realtime_monitor import RealTimeMonitor


class ScalingLauncher:
    """Unified launcher for scaling operations"""
    
    def __init__(self):
        self.config_manager = ScalingConfigManager()
        self.output_dir = "scaling_results"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def print_banner(self):
        """Print application banner"""
        print("🚀 WhatsApp Analysis Scaling Suite")
        print("=" * 60)
        print("Advanced scaling tools for large-scale WhatsApp analysis")
        print("- Scalable data extraction with progress tracking")
        print("- Real-time opportunity monitoring")
        print("- Intelligent configuration management")
        print("- Performance optimization")
        print("=" * 60)
    
    def print_main_menu(self):
        """Print main menu options"""
        print("\n📋 SCALING OPERATIONS:")
        print("1. 📊 Large-Scale Data Extraction")
        print("2. 🔴 Real-Time Monitoring")
        print("3. ⚙️  Configuration Management")
        print("4. 📈 Performance Analysis")
        print("5. 🔧 System Diagnostics")
        print("6. 📚 Help & Documentation")
        print("0. 🚪 Exit")
    
    async def run_scalable_extraction(self, args):
        """Run large-scale data extraction"""
        print("\n🎯 LARGE-SCALE DATA EXTRACTION")
        print("=" * 50)
        
        config = self.config_manager.get_extraction_config()
        
        # Override with command line arguments
        max_chats = args.max_chats or config.max_chats
        max_messages = args.max_messages or config.max_messages_per_chat
        
        print(f"Configuration:")
        print(f"  Max Chats: {max_chats}")
        print(f"  Max Messages/Chat: {max_messages}")
        print(f"  Batch Size: {config.batch_size}")
        print(f"  Rate Limiting: {config.chat_delay_seconds}s between chats")
        
        # Estimate resources
        estimates = self.config_manager.estimate_resource_usage()
        print(f"\nEstimated Resources:")
        print(f"  Total Messages: ~{estimates['estimated_messages']:,}")
        print(f"  Memory Usage: ~{estimates['estimated_memory_mb']} MB")
        print(f"  Disk Usage: ~{estimates['estimated_disk_mb']} MB")
        print(f"  Estimated Time: ~{estimates['estimated_time_minutes']} minutes")
        
        if not estimates['within_memory_limit']:
            print("⚠️ Warning: Estimated memory usage exceeds configured limit")
        
        if not estimates['within_disk_limit']:
            print("⚠️ Warning: Estimated disk usage exceeds configured limit")
        
        # Confirm before proceeding
        if not args.yes:
            response = input("\nProceed with extraction? (y/N): ")
            if response.lower() != 'y':
                print("❌ Extraction cancelled")
                return False
        
        # Run extraction
        extractor = ScalableExtractor()
        
        # Apply configuration
        extractor.chat_delay = config.chat_delay_seconds
        extractor.message_delay = config.message_delay_seconds
        extractor.batch_size = config.batch_size
        
        success = await extractor.run_scalable_extraction(max_chats, max_messages)
        
        if success:
            print("\n✅ Large-scale extraction completed successfully!")
            print(f"📁 Results saved to: {os.path.abspath(extractor.output_dir)}")
        else:
            print("\n❌ Large-scale extraction failed")
        
        return success
    
    async def run_realtime_monitoring(self, args):
        """Run real-time monitoring"""
        print("\n🔴 REAL-TIME MONITORING")
        print("=" * 50)
        
        config = self.config_manager.get_monitoring_config()
        
        # Override with command line arguments
        duration = args.duration or config.monitor_duration_minutes
        interval = args.interval or config.check_interval_seconds
        threshold = args.threshold or config.opportunity_threshold
        
        print(f"Configuration:")
        print(f"  Check Interval: {interval} seconds")
        print(f"  Opportunity Threshold: {threshold}")
        print(f"  Duration: {'Indefinite' if duration is None else f'{duration} minutes'}")
        print(f"  Alert System: {'Enabled' if config.enable_dashboard else 'Disabled'}")
        
        # Confirm before proceeding
        if not args.yes:
            response = input("\nStart real-time monitoring? (y/N): ")
            if response.lower() != 'y':
                print("❌ Monitoring cancelled")
                return False
        
        # Run monitoring
        monitor = RealTimeMonitor()
        
        # Apply configuration
        monitor.monitor_interval = interval
        monitor.opportunity_threshold = threshold
        monitor.max_history_size = config.max_history_size
        
        success = await monitor.start_monitoring(duration)
        
        if success:
            print("\n✅ Real-time monitoring completed successfully!")
            print(f"📁 Results saved to: {os.path.abspath(monitor.output_dir)}")
        else:
            print("\n❌ Real-time monitoring failed")
        
        return success
    
    def run_configuration_management(self, args):
        """Run configuration management"""
        print("\n⚙️ CONFIGURATION MANAGEMENT")
        print("=" * 50)
        
        if args.preset:
            self.config_manager.create_preset_config(args.preset)
            print(f"✅ Applied '{args.preset}' configuration preset")
        
        if args.show_config:
            self.config_manager.print_config_summary()
        
        if args.validate_config:
            warnings = self.config_manager.validate_config()
            if warnings:
                print("\n⚠️ Configuration Warnings:")
                for warning in warnings:
                    print(f"  {warning}")
            else:
                print("\n✅ Configuration is valid")
        
        if args.estimate_resources:
            estimates = self.config_manager.estimate_resource_usage()
            print("\n📊 Resource Usage Estimates:")
            print(f"  Messages: {estimates['estimated_messages']:,}")
            print(f"  Memory: {estimates['estimated_memory_mb']} MB")
            print(f"  Disk: {estimates['estimated_disk_mb']} MB")
            print(f"  Time: {estimates['estimated_time_minutes']} minutes")
            print(f"  Memory OK: {'✅' if estimates['within_memory_limit'] else '❌'}")
            print(f"  Disk OK: {'✅' if estimates['within_disk_limit'] else '❌'}")
        
        # Interactive configuration if no specific action
        if not any([args.preset, args.show_config, args.validate_config, args.estimate_resources]):
            self.interactive_configuration()
    
    def interactive_configuration(self):
        """Interactive configuration management"""
        while True:
            print("\n⚙️ Configuration Options:")
            print("1. Show current configuration")
            print("2. Apply preset configuration")
            print("3. Validate configuration")
            print("4. Estimate resource usage")
            print("5. Update extraction settings")
            print("6. Update monitoring settings")
            print("0. Back to main menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self.config_manager.print_config_summary()
            
            elif choice == "2":
                print("\nAvailable presets:")
                print("  light - Minimal resource usage")
                print("  standard - Balanced performance")
                print("  heavy - Maximum data extraction")
                print("  enterprise - Maximum performance")
                
                preset = input("Enter preset name: ").strip()
                if preset in ["light", "standard", "heavy", "enterprise"]:
                    self.config_manager.create_preset_config(preset)
                    print(f"✅ Applied '{preset}' preset")
                else:
                    print("❌ Invalid preset name")
            
            elif choice == "3":
                warnings = self.config_manager.validate_config()
                if warnings:
                    print("\n⚠️ Configuration Warnings:")
                    for warning in warnings:
                        print(f"  {warning}")
                else:
                    print("\n✅ Configuration is valid")
            
            elif choice == "4":
                estimates = self.config_manager.estimate_resource_usage()
                print("\n📊 Resource Usage Estimates:")
                print(f"  Messages: {estimates['estimated_messages']:,}")
                print(f"  Memory: {estimates['estimated_memory_mb']} MB")
                print(f"  Disk: {estimates['estimated_disk_mb']} MB")
                print(f"  Time: {estimates['estimated_time_minutes']} minutes")
            
            elif choice == "5":
                self.update_extraction_settings()
            
            elif choice == "6":
                self.update_monitoring_settings()
            
            elif choice == "0":
                break
            
            else:
                print("❌ Invalid option")
    
    def update_extraction_settings(self):
        """Update extraction settings interactively"""
        config = self.config_manager.get_extraction_config()
        
        print(f"\nCurrent Extraction Settings:")
        print(f"  Max Chats: {config.max_chats}")
        print(f"  Max Messages/Chat: {config.max_messages_per_chat}")
        print(f"  Batch Size: {config.batch_size}")
        print(f"  Chat Delay: {config.chat_delay_seconds}s")
        
        try:
            max_chats = input(f"Max Chats [{config.max_chats}]: ").strip()
            if max_chats:
                self.config_manager.update_extraction_config(max_chats=int(max_chats))
            
            max_messages = input(f"Max Messages/Chat [{config.max_messages_per_chat}]: ").strip()
            if max_messages:
                self.config_manager.update_extraction_config(max_messages_per_chat=int(max_messages))
            
            batch_size = input(f"Batch Size [{config.batch_size}]: ").strip()
            if batch_size:
                self.config_manager.update_extraction_config(batch_size=int(batch_size))
            
            chat_delay = input(f"Chat Delay (seconds) [{config.chat_delay_seconds}]: ").strip()
            if chat_delay:
                self.config_manager.update_extraction_config(chat_delay_seconds=float(chat_delay))
            
            print("✅ Extraction settings updated")
            
        except ValueError:
            print("❌ Invalid input - settings not updated")
    
    def update_monitoring_settings(self):
        """Update monitoring settings interactively"""
        config = self.config_manager.get_monitoring_config()
        
        print(f"\nCurrent Monitoring Settings:")
        print(f"  Check Interval: {config.check_interval_seconds}s")
        print(f"  Opportunity Threshold: {config.opportunity_threshold}")
        print(f"  Max History: {config.max_history_size}")
        
        try:
            interval = input(f"Check Interval (seconds) [{config.check_interval_seconds}]: ").strip()
            if interval:
                self.config_manager.update_monitoring_config(check_interval_seconds=int(interval))
            
            threshold = input(f"Opportunity Threshold [{config.opportunity_threshold}]: ").strip()
            if threshold:
                self.config_manager.update_monitoring_config(opportunity_threshold=int(threshold))
            
            history = input(f"Max History Size [{config.max_history_size}]: ").strip()
            if history:
                self.config_manager.update_monitoring_config(max_history_size=int(history))
            
            print("✅ Monitoring settings updated")
            
        except ValueError:
            print("❌ Invalid input - settings not updated")
    
    def run_performance_analysis(self):
        """Run performance analysis"""
        print("\n📈 PERFORMANCE ANALYSIS")
        print("=" * 50)
        
        # System information
        import psutil
        
        print("💻 System Information:")
        print(f"  CPU Cores: {psutil.cpu_count()}")
        print(f"  Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        print(f"  Available Memory: {psutil.virtual_memory().available / (1024**3):.1f} GB")
        print(f"  Disk Free: {psutil.disk_usage('.').free / (1024**3):.1f} GB")
        
        # Configuration analysis
        config = self.config_manager
        estimates = config.estimate_resource_usage()
        
        print("\n📊 Configuration Analysis:")
        print(f"  Estimated Messages: {estimates['estimated_messages']:,}")
        print(f"  Estimated Memory: {estimates['estimated_memory_mb']} MB")
        print(f"  Estimated Time: {estimates['estimated_time_minutes']} minutes")
        
        # Performance recommendations
        print("\n💡 Performance Recommendations:")
        
        if estimates['estimated_memory_mb'] > 1000:
            print("  • Consider reducing max_chats or max_messages_per_chat")
        
        if config.extraction.chat_delay_seconds < 1.0:
            print("  • Consider increasing chat_delay to avoid rate limiting")
        
        if config.performance.max_concurrent_requests > 10:
            print("  • High concurrency may overwhelm the server")
        
        if estimates['estimated_time_minutes'] > 60:
            print("  • Consider running extraction in smaller batches")
        
        # Validation warnings
        warnings = config.validate_config()
        if warnings:
            print("\n⚠️ Configuration Warnings:")
            for warning in warnings:
                print(f"  {warning}")
    
    def run_system_diagnostics(self):
        """Run system diagnostics"""
        print("\n🔧 SYSTEM DIAGNOSTICS")
        print("=" * 50)
        
        # Check dependencies
        print("📦 Dependency Check:")
        required_modules = ['asyncio', 'json', 'psutil', 'aiohttp']
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"  ✅ {module}")
            except ImportError:
                print(f"  ❌ {module} - Missing")
        
        # Check MCP server
        server_path = r"C:\Users\elie\OneDrive\Documents\Cline\MCP\whatsapp-mcp\whatsapp-mcp-server\main.py"
        print(f"\n🔌 MCP Server Check:")
        if os.path.exists(server_path):
            print(f"  ✅ Server found: {server_path}")
        else:
            print(f"  ❌ Server not found: {server_path}")
        
        # Check output directories
        print(f"\n📁 Directory Check:")
        directories = [
            "scalable_extracted_data",
            "realtime_monitoring",
            "scaling_results"
        ]
        
        for directory in directories:
            if os.path.exists(directory):
                print(f"  ✅ {directory}")
            else:
                print(f"  ⚠️ {directory} - Will be created")
        
        # Configuration check
        print(f"\n⚙️ Configuration Check:")
        warnings = self.config_manager.validate_config()
        if warnings:
            print(f"  ⚠️ {len(warnings)} warnings found")
            for warning in warnings:
                print(f"    {warning}")
        else:
            print(f"  ✅ Configuration is valid")
    
    def show_help(self):
        """Show help and documentation"""
        print("\n📚 HELP & DOCUMENTATION")
        print("=" * 50)
        
        print("🎯 SCALING OPERATIONS:")
        print("  Large-Scale Extraction:")
        print("    Extract data from hundreds of chats with thousands of messages")
        print("    Features: Progress tracking, batch processing, rate limiting")
        print("    Usage: python scaling_launcher.py extract --max-chats 100")
        
        print("\n  Real-Time Monitoring:")
        print("    Continuously monitor for new opportunities")
        print("    Features: Live alerts, dashboard, trend analysis")
        print("    Usage: python scaling_launcher.py monitor --duration 60")
        
        print("\n⚙️ CONFIGURATION:")
        print("  Presets: light, standard, heavy, enterprise")
        print("  Usage: python scaling_launcher.py config --preset standard")
        
        print("\n📊 EXAMPLES:")
        print("  # Extract 200 chats with 500 messages each")
        print("  python scaling_launcher.py extract --max-chats 200 --max-messages 500")
        
        print("\n  # Monitor for 2 hours with 15-second intervals")
        print("  python scaling_launcher.py monitor --duration 120 --interval 15")
        
        print("\n  # Apply enterprise configuration")
        print("  python scaling_launcher.py config --preset enterprise")
        
        print("\n📁 OUTPUT FILES:")
        print("  scalable_extracted_data/ - Large-scale extraction results")
        print("  realtime_monitoring/ - Real-time monitoring data")
        print("  scaling_results/ - Combined analysis results")


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="WhatsApp Analysis Scaling Suite")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Large-scale data extraction')
    extract_parser.add_argument('--max-chats', type=int, help='Maximum chats to process')
    extract_parser.add_argument('--max-messages', type=int, help='Maximum messages per chat')
    extract_parser.add_argument('--yes', action='store_true', help='Skip confirmation prompts')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Real-time monitoring')
    monitor_parser.add_argument('--duration', type=int, help='Monitoring duration in minutes')
    monitor_parser.add_argument('--interval', type=int, help='Check interval in seconds')
    monitor_parser.add_argument('--threshold', type=int, help='Opportunity threshold')
    monitor_parser.add_argument('--yes', action='store_true', help='Skip confirmation prompts')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--preset', choices=['light', 'standard', 'heavy', 'enterprise'], 
                              help='Apply preset configuration')
    config_parser.add_argument('--show-config', action='store_true', help='Show current configuration')
    config_parser.add_argument('--validate-config', action='store_true', help='Validate configuration')
    config_parser.add_argument('--estimate-resources', action='store_true', help='Estimate resource usage')
    
    # Performance command
    perf_parser = subparsers.add_parser('performance', help='Performance analysis')
    
    # Diagnostics command
    diag_parser = subparsers.add_parser('diagnostics', help='System diagnostics')
    
    # Help command
    help_parser = subparsers.add_parser('help', help='Show help and documentation')
    
    args = parser.parse_args()
    
    launcher = ScalingLauncher()
    launcher.print_banner()
    
    try:
        if args.command == 'extract':
            return 0 if await launcher.run_scalable_extraction(args) else 1
        
        elif args.command == 'monitor':
            return 0 if await launcher.run_realtime_monitoring(args) else 1
        
        elif args.command == 'config':
            launcher.run_configuration_management(args)
            return 0
        
        elif args.command == 'performance':
            launcher.run_performance_analysis()
            return 0
        
        elif args.command == 'diagnostics':
            launcher.run_system_diagnostics()
            return 0
        
        elif args.command == 'help':
            launcher.show_help()
            return 0
        
        else:
            # Interactive mode
            launcher.print_main_menu()
            return 0
            
    except KeyboardInterrupt:
        print("\n⏹️ Operation interrupted")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))