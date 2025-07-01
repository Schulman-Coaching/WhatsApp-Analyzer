#!/usr/bin/env python3
"""
MCP Configuration Management

This module provides configuration management for MCP clients,
including server endpoints, authentication, and connection settings.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MCPServerSettings:
    """Settings for an MCP server connection"""
    name: str
    endpoint: str
    connection_type: str = "sse"  # sse, websocket, stdio
    auth_token: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    health_check_interval: int = 60
    session_timeout: int = 3600
    custom_headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.custom_headers is None:
            self.custom_headers = {}


@dataclass
class WhatsAppMCPSettings:
    """WhatsApp-specific MCP settings"""
    server: MCPServerSettings
    rate_limits: Dict[str, int] = None
    auto_authenticate: bool = False
    phone_number: Optional[str] = None
    session_persistence: bool = True
    export_format: str = "json"
    include_media: bool = False
    
    def __post_init__(self):
        if self.rate_limits is None:
            self.rate_limits = {
                "messages_per_minute": 60,
                "chats_per_minute": 30,
                "requests_per_second": 2,
                "burst_limit": 10,
                "cooldown_period": 300
            }


class MCPConfig:
    """Configuration manager for MCP clients"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "mcp_config.json"
        self.config_path = Path(self.config_file)
        self._config: Dict[str, Any] = {}
        self._whatsapp_settings: Optional[WhatsAppMCPSettings] = None
        
        # Load configuration
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file or environment variables"""
        # Try to load from file first
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.info(f"Loaded MCP configuration from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config file {self.config_path}: {e}")
                self._config = {}
        
        # Override with environment variables if present
        self._load_from_environment()
        
        # Set defaults if no configuration found
        if not self._config:
            self._set_default_config()
        
        # Parse WhatsApp settings
        self._parse_whatsapp_settings()
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables"""
        env_mapping = {
            "MCP_WHATSAPP_ENDPOINT": ("whatsapp", "server", "endpoint"),
            "MCP_WHATSAPP_CONNECTION_TYPE": ("whatsapp", "server", "connection_type"),
            "MCP_WHATSAPP_AUTH_TOKEN": ("whatsapp", "server", "auth_token"),
            "MCP_WHATSAPP_TIMEOUT": ("whatsapp", "server", "timeout"),
            "MCP_WHATSAPP_MAX_RETRIES": ("whatsapp", "server", "max_retries"),
            "MCP_WHATSAPP_PHONE_NUMBER": ("whatsapp", "phone_number"),
            "MCP_WHATSAPP_AUTO_AUTH": ("whatsapp", "auto_authenticate"),
        }
        
        for env_var, config_path in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Navigate to the nested config location
                current = self._config
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # Convert value to appropriate type
                final_key = config_path[-1]
                if final_key in ["timeout", "max_retries"]:
                    current[final_key] = int(value)
                elif final_key == "auto_authenticate":
                    current[final_key] = value.lower() in ("true", "1", "yes")
                else:
                    current[final_key] = value
    
    def _set_default_config(self) -> None:
        """Set default configuration values"""
        self._config = {
            "whatsapp": {
                "server": {
                    "name": "github.com/lharries/whatsapp-mcp",
                    "endpoint": "http://localhost:3000",
                    "connection_type": "sse",
                    "timeout": 60,
                    "max_retries": 5,
                    "retry_delay": 2.0,
                    "health_check_interval": 30,
                    "session_timeout": 7200,
                    "custom_headers": {
                        "User-Agent": "WhatsApp-MCP-Client/1.0",
                        "Accept": "application/json"
                    }
                },
                "rate_limits": {
                    "messages_per_minute": 60,
                    "chats_per_minute": 30,
                    "requests_per_second": 2,
                    "burst_limit": 10,
                    "cooldown_period": 300
                },
                "auto_authenticate": False,
                "session_persistence": True,
                "export_format": "json",
                "include_media": False
            }
        }
        logger.info("Using default MCP configuration")
    
    def _parse_whatsapp_settings(self) -> None:
        """Parse WhatsApp-specific settings from configuration"""
        try:
            whatsapp_config = self._config.get("whatsapp", {})
            server_config = whatsapp_config.get("server", {})
            
            server_settings = MCPServerSettings(
                name=server_config.get("name", "github.com/lharries/whatsapp-mcp"),
                endpoint=server_config.get("endpoint", "http://localhost:3000"),
                connection_type=server_config.get("connection_type", "sse"),
                auth_token=server_config.get("auth_token"),
                timeout=server_config.get("timeout", 60),
                max_retries=server_config.get("max_retries", 5),
                retry_delay=server_config.get("retry_delay", 2.0),
                health_check_interval=server_config.get("health_check_interval", 30),
                session_timeout=server_config.get("session_timeout", 7200),
                custom_headers=server_config.get("custom_headers", {})
            )
            
            self._whatsapp_settings = WhatsAppMCPSettings(
                server=server_settings,
                rate_limits=whatsapp_config.get("rate_limits", {}),
                auto_authenticate=whatsapp_config.get("auto_authenticate", False),
                phone_number=whatsapp_config.get("phone_number"),
                session_persistence=whatsapp_config.get("session_persistence", True),
                export_format=whatsapp_config.get("export_format", "json"),
                include_media=whatsapp_config.get("include_media", False)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse WhatsApp settings: {e}")
            # Fall back to default settings
            self._set_default_config()
            self._parse_whatsapp_settings()
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved MCP configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config file: {e}")
    
    def get_whatsapp_settings(self) -> WhatsAppMCPSettings:
        """Get WhatsApp MCP settings"""
        if self._whatsapp_settings is None:
            self._parse_whatsapp_settings()
        return self._whatsapp_settings
    
    def update_whatsapp_settings(self, **kwargs) -> None:
        """Update WhatsApp settings"""
        if self._whatsapp_settings is None:
            self._parse_whatsapp_settings()
        
        # Update the settings object
        for key, value in kwargs.items():
            if hasattr(self._whatsapp_settings, key):
                setattr(self._whatsapp_settings, key, value)
            elif hasattr(self._whatsapp_settings.server, key):
                setattr(self._whatsapp_settings.server, key, value)
        
        # Update the internal config dict
        self._update_config_from_settings()
    
    def _update_config_from_settings(self) -> None:
        """Update internal config dict from settings objects"""
        if self._whatsapp_settings:
            self._config["whatsapp"] = {
                "server": asdict(self._whatsapp_settings.server),
                "rate_limits": self._whatsapp_settings.rate_limits,
                "auto_authenticate": self._whatsapp_settings.auto_authenticate,
                "phone_number": self._whatsapp_settings.phone_number,
                "session_persistence": self._whatsapp_settings.session_persistence,
                "export_format": self._whatsapp_settings.export_format,
                "include_media": self._whatsapp_settings.include_media
            }
    
    def get_config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary"""
        return self._config.copy()
    
    def create_sample_config(self, output_path: str = "mcp_config_sample.json") -> None:
        """Create a sample configuration file"""
        sample_config = {
            "whatsapp": {
                "server": {
                    "name": "github.com/lharries/whatsapp-mcp",
                    "endpoint": "http://localhost:3000",
                    "connection_type": "sse",
                    "auth_token": None,
                    "timeout": 60,
                    "max_retries": 5,
                    "retry_delay": 2.0,
                    "health_check_interval": 30,
                    "session_timeout": 7200,
                    "custom_headers": {
                        "User-Agent": "WhatsApp-MCP-Client/1.0",
                        "Accept": "application/json"
                    }
                },
                "rate_limits": {
                    "messages_per_minute": 60,
                    "chats_per_minute": 30,
                    "requests_per_second": 2,
                    "burst_limit": 10,
                    "cooldown_period": 300
                },
                "auto_authenticate": False,
                "phone_number": None,
                "session_persistence": True,
                "export_format": "json",
                "include_media": False
            }
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, indent=2, ensure_ascii=False)
            logger.info(f"Created sample configuration file: {output_path}")
        except Exception as e:
            logger.error(f"Failed to create sample config: {e}")


# Global configuration instance
_global_config: Optional[MCPConfig] = None


def get_mcp_config(config_file: Optional[str] = None) -> MCPConfig:
    """Get the global MCP configuration instance"""
    global _global_config
    if _global_config is None or config_file is not None:
        _global_config = MCPConfig(config_file)
    return _global_config


def get_whatsapp_settings() -> WhatsAppMCPSettings:
    """Get WhatsApp MCP settings from global configuration"""
    config = get_mcp_config()
    return config.get_whatsapp_settings()


if __name__ == "__main__":
    # Create a sample configuration file when run directly
    config = MCPConfig()
    config.create_sample_config()
    print("Sample configuration file created: mcp_config_sample.json")
    print("Copy this to mcp_config.json and customize as needed.")