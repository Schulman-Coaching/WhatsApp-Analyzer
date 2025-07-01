#!/usr/bin/env python3
"""
Scaling Configuration Management

This module provides configuration management for large-scale WhatsApp analysis:
- Performance tuning parameters
- Rate limiting configurations
- Resource management settings
- Monitoring thresholds
- Alert configurations
"""

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ExtractionConfig:
    """Configuration for data extraction scaling"""
    max_chats: int = 100
    max_messages_per_chat: int = 500
    batch_size: int = 10
    chat_delay_seconds: float = 2.0
    message_delay_seconds: float = 1.0
    retry_attempts: int = 3
    retry_delay_seconds: float = 5.0
    enable_progress_tracking: bool = True
    save_individual_chats: bool = True
    incremental_save_frequency: int = 3  # Every N batches


@dataclass
class MonitoringConfig:
    """Configuration for real-time monitoring"""
    check_interval_seconds: int = 30
    opportunity_threshold: int = 2
    max_history_size: int = 1000
    alert_cooldown_minutes: int = 5
    high_value_score_threshold: int = 5
    enable_dashboard: bool = True
    save_frequency_cycles: int = 10
    monitor_duration_minutes: Optional[int] = None


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization"""
    max_concurrent_requests: int = 5
    connection_timeout_seconds: int = 30
    read_timeout_seconds: int = 60
    max_retries: int = 3
    backoff_factor: float = 2.0
    enable_connection_pooling: bool = True
    memory_limit_mb: int = 1024
    disk_cache_size_mb: int = 512


@dataclass
class AlertConfig:
    """Configuration for opportunity alerts"""
    enable_alerts: bool = True
    urgent_keywords: list = None
    business_keywords: list = None
    service_keywords: list = None
    product_keywords: list = None
    networking_keywords: list = None
    keyword_weights: Dict[str, int] = None
    min_alert_score: int = 2
    max_alerts_per_hour: int = 50
    
    def __post_init__(self):
        if self.urgent_keywords is None:
            self.urgent_keywords = ["urgent", "asap", "immediately", "emergency", "critical"]
        
        if self.business_keywords is None:
            self.business_keywords = ["business", "startup", "investment", "funding", "revenue", "profit", "money"]
        
        if self.service_keywords is None:
            self.service_keywords = ["hire", "looking for", "need help", "recommend", "service", "consultant", "expert"]
        
        if self.product_keywords is None:
            self.product_keywords = ["buy", "sell", "purchase", "product", "deal", "discount", "offer", "price"]
        
        if self.networking_keywords is None:
            self.networking_keywords = ["connect", "introduce", "meeting", "collaboration", "partner", "network"]
        
        if self.keyword_weights is None:
            self.keyword_weights = {
                "urgent": 3,
                "business": 2,
                "services": 2,
                "products": 1,
                "networking": 1
            }


@dataclass
class ResourceConfig:
    """Configuration for resource management"""
    max_memory_usage_mb: int = 2048
    max_disk_usage_gb: int = 10
    cleanup_old_files_days: int = 30
    compress_old_data: bool = True
    enable_resource_monitoring: bool = True
    auto_cleanup: bool = True
    log_level: str = "INFO"
    max_log_file_size_mb: int = 100


class ScalingConfigManager:
    """Manager for scaling configuration"""
    
    def __init__(self, config_file: str = "scaling_config.json"):
        self.config_file = config_file
        self.extraction = ExtractionConfig()
        self.monitoring = MonitoringConfig()
        self.performance = PerformanceConfig()
        self.alerts = AlertConfig()
        self.resources = ResourceConfig()
        
        # Load existing config if available
        self.load_config()
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            self.save_config()  # Create default config
            return False
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update configurations
            if "extraction" in config_data:
                self.extraction = ExtractionConfig(**config_data["extraction"])
            
            if "monitoring" in config_data:
                self.monitoring = MonitoringConfig(**config_data["monitoring"])
            
            if "performance" in config_data:
                self.performance = PerformanceConfig(**config_data["performance"])
            
            if "alerts" in config_data:
                self.alerts = AlertConfig(**config_data["alerts"])
            
            if "resources" in config_data:
                self.resources = ResourceConfig(**config_data["resources"])
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
            return False
    
    def save_config(self):
        """Save configuration to file"""
        config_data = {
            "extraction": asdict(self.extraction),
            "monitoring": asdict(self.monitoring),
            "performance": asdict(self.performance),
            "alerts": asdict(self.alerts),
            "resources": asdict(self.resources),
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def get_extraction_config(self) -> ExtractionConfig:
        """Get extraction configuration"""
        return self.extraction
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration"""
        return self.monitoring
    
    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration"""
        return self.performance
    
    def get_alert_config(self) -> AlertConfig:
        """Get alert configuration"""
        return self.alerts
    
    def get_resource_config(self) -> ResourceConfig:
        """Get resource configuration"""
        return self.resources
    
    def update_extraction_config(self, **kwargs):
        """Update extraction configuration"""
        for key, value in kwargs.items():
            if hasattr(self.extraction, key):
                setattr(self.extraction, key, value)
        self.save_config()
    
    def update_monitoring_config(self, **kwargs):
        """Update monitoring configuration"""
        for key, value in kwargs.items():
            if hasattr(self.monitoring, key):
                setattr(self.monitoring, key, value)
        self.save_config()
    
    def update_performance_config(self, **kwargs):
        """Update performance configuration"""
        for key, value in kwargs.items():
            if hasattr(self.performance, key):
                setattr(self.performance, key, value)
        self.save_config()
    
    def update_alert_config(self, **kwargs):
        """Update alert configuration"""
        for key, value in kwargs.items():
            if hasattr(self.alerts, key):
                setattr(self.alerts, key, value)
        self.save_config()
    
    def update_resource_config(self, **kwargs):
        """Update resource configuration"""
        for key, value in kwargs.items():
            if hasattr(self.resources, key):
                setattr(self.resources, key, value)
        self.save_config()
    
    def create_preset_config(self, preset: str):
        """Create preset configurations for different use cases"""
        if preset == "light":
            # Light usage - minimal resource consumption
            self.extraction.max_chats = 20
            self.extraction.max_messages_per_chat = 100
            self.extraction.batch_size = 5
            self.extraction.chat_delay_seconds = 3.0
            self.monitoring.check_interval_seconds = 60
            self.performance.max_concurrent_requests = 2
            
        elif preset == "standard":
            # Standard usage - balanced performance
            self.extraction.max_chats = 50
            self.extraction.max_messages_per_chat = 200
            self.extraction.batch_size = 10
            self.extraction.chat_delay_seconds = 2.0
            self.monitoring.check_interval_seconds = 30
            self.performance.max_concurrent_requests = 5
            
        elif preset == "heavy":
            # Heavy usage - maximum data extraction
            self.extraction.max_chats = 200
            self.extraction.max_messages_per_chat = 1000
            self.extraction.batch_size = 20
            self.extraction.chat_delay_seconds = 1.0
            self.monitoring.check_interval_seconds = 15
            self.performance.max_concurrent_requests = 10
            
        elif preset == "enterprise":
            # Enterprise usage - maximum performance
            self.extraction.max_chats = 500
            self.extraction.max_messages_per_chat = 2000
            self.extraction.batch_size = 50
            self.extraction.chat_delay_seconds = 0.5
            self.monitoring.check_interval_seconds = 10
            self.performance.max_concurrent_requests = 20
            self.performance.memory_limit_mb = 4096
            self.resources.max_memory_usage_mb = 8192
            
        self.save_config()
        print(f"✅ Applied '{preset}' preset configuration")
    
    def validate_config(self) -> List[str]:
        """Validate configuration settings"""
        warnings = []
        
        # Extraction validation
        if self.extraction.max_chats > 1000:
            warnings.append("⚠️ Very high max_chats may cause performance issues")
        
        if self.extraction.chat_delay_seconds < 0.5:
            warnings.append("⚠️ Very low chat_delay may trigger rate limiting")
        
        if self.extraction.batch_size > 50:
            warnings.append("⚠️ Large batch_size may cause memory issues")
        
        # Monitoring validation
        if self.monitoring.check_interval_seconds < 10:
            warnings.append("⚠️ Very frequent monitoring may impact performance")
        
        # Performance validation
        if self.performance.max_concurrent_requests > 20:
            warnings.append("⚠️ High concurrency may overwhelm the server")
        
        # Resource validation
        if self.resources.max_memory_usage_mb < 512:
            warnings.append("⚠️ Low memory limit may cause processing failures")
        
        return warnings
    
    def print_config_summary(self):
        """Print configuration summary"""
        print("📋 SCALING CONFIGURATION SUMMARY")
        print("=" * 50)
        
        print(f"\n📊 EXTRACTION:")
        print(f"  Max Chats: {self.extraction.max_chats}")
        print(f"  Max Messages/Chat: {self.extraction.max_messages_per_chat}")
        print(f"  Batch Size: {self.extraction.batch_size}")
        print(f"  Chat Delay: {self.extraction.chat_delay_seconds}s")
        
        print(f"\n🔍 MONITORING:")
        print(f"  Check Interval: {self.monitoring.check_interval_seconds}s")
        print(f"  Opportunity Threshold: {self.monitoring.opportunity_threshold}")
        print(f"  History Size: {self.monitoring.max_history_size}")
        
        print(f"\n⚡ PERFORMANCE:")
        print(f"  Max Concurrent: {self.performance.max_concurrent_requests}")
        print(f"  Connection Timeout: {self.performance.connection_timeout_seconds}s")
        print(f"  Memory Limit: {self.performance.memory_limit_mb}MB")
        
        print(f"\n🚨 ALERTS:")
        print(f"  Enabled: {self.alerts.enable_alerts}")
        print(f"  Min Score: {self.alerts.min_alert_score}")
        print(f"  Max/Hour: {self.alerts.max_alerts_per_hour}")
        
        print(f"\n💾 RESOURCES:")
        print(f"  Max Memory: {self.resources.max_memory_usage_mb}MB")
        print(f"  Max Disk: {self.resources.max_disk_usage_gb}GB")
        print(f"  Auto Cleanup: {self.resources.auto_cleanup}")
        
        # Show warnings
        warnings = self.validate_config()
        if warnings:
            print(f"\n⚠️ CONFIGURATION WARNINGS:")
            for warning in warnings:
                print(f"  {warning}")
    
    def estimate_resource_usage(self) -> Dict[str, Any]:
        """Estimate resource usage based on configuration"""
        # Rough estimates based on configuration
        estimated_messages = self.extraction.max_chats * self.extraction.max_messages_per_chat
        estimated_memory_mb = (estimated_messages * 0.001) + 100  # ~1KB per message + overhead
        estimated_disk_mb = estimated_messages * 0.002  # ~2KB per message stored
        estimated_time_minutes = (
            self.extraction.max_chats * self.extraction.chat_delay_seconds + 
            estimated_messages * self.extraction.message_delay_seconds
        ) / 60
        
        return {
            "estimated_messages": estimated_messages,
            "estimated_memory_mb": round(estimated_memory_mb, 1),
            "estimated_disk_mb": round(estimated_disk_mb, 1),
            "estimated_time_minutes": round(estimated_time_minutes, 1),
            "within_memory_limit": estimated_memory_mb <= self.performance.memory_limit_mb,
            "within_disk_limit": estimated_disk_mb <= (self.resources.max_disk_usage_gb * 1024)
        }


def main():
    """Main function for configuration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scaling configuration management")
    parser.add_argument("--preset", choices=["light", "standard", "heavy", "enterprise"], 
                       help="Apply preset configuration")
    parser.add_argument("--show", action="store_true", help="Show current configuration")
    parser.add_argument("--estimate", action="store_true", help="Show resource usage estimates")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    
    args = parser.parse_args()
    
    config_manager = ScalingConfigManager()
    
    if args.preset:
        config_manager.create_preset_config(args.preset)
        print(f"✅ Applied '{args.preset}' configuration preset")
    
    if args.show:
        config_manager.print_config_summary()
    
    if args.estimate:
        estimates = config_manager.estimate_resource_usage()
        print("\n📊 RESOURCE USAGE ESTIMATES:")
        print(f"  Messages: {estimates['estimated_messages']:,}")
        print(f"  Memory: {estimates['estimated_memory_mb']} MB")
        print(f"  Disk: {estimates['estimated_disk_mb']} MB")
        print(f"  Time: {estimates['estimated_time_minutes']} minutes")
        print(f"  Memory OK: {'✅' if estimates['within_memory_limit'] else '❌'}")
        print(f"  Disk OK: {'✅' if estimates['within_disk_limit'] else '❌'}")
    
    if args.validate:
        warnings = config_manager.validate_config()
        if warnings:
            print("\n⚠️ CONFIGURATION WARNINGS:")
            for warning in warnings:
                print(f"  {warning}")
        else:
            print("\n✅ Configuration is valid")
    
    if not any([args.preset, args.show, args.estimate, args.validate]):
        config_manager.print_config_summary()


if __name__ == "__main__":
    main()