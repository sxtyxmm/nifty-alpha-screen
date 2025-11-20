"""Configuration Management Module"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    """Configuration manager for NSE Stock Analysis System"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self.load_config()
    
    def load_config(self, config_path: str = None):
        """Load configuration from YAML file"""
        if config_path is None:
            # Default to config/settings.yaml
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "settings.yaml"
        
        try:
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f)
        except FileNotFoundError:
            # Fallback to default configuration
            self._config = self._get_default_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key (e.g., 'app.name')"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        # Override with environment variables
        env_key = '_'.join(keys).upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            # Try to convert to appropriate type
            if isinstance(value, bool):
                return env_value.lower() in ('true', '1', 'yes')
            elif isinstance(value, int):
                return int(env_value)
            elif isinstance(value, float):
                return float(env_value)
            return env_value
        
        return value
    
    def get_all(self) -> Dict:
        """Get entire configuration dictionary"""
        return self._config.copy()
    
    @staticmethod
    def _get_default_config() -> Dict:
        """Return default configuration if YAML file not found"""
        return {
            'app': {
                'name': 'NSE Stock Analysis System',
                'version': '2.0.0',
                'environment': 'production'
            },
            'data_fetching': {
                'max_workers': 10,
                'timeout': 30,
                'retry_attempts': 3,
                'retry_delay': 2,
                'cache_ttl': 3600
            },
            'technical_analysis': {
                'ema_period': 44,
                'price_history_days': 365,
                'slope_days': 5
            },
            'scoring': {
                'signals': {
                    'buy_threshold': 3.0,
                    'hold_min': 1.0,
                    'hold_max': 2.9
                }
            },
            'logging': {
                'level': 'INFO',
                'file_path': 'logs/nse_analysis.log'
            }
        }


# Global config instance
config = Config()


# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config.get(key, default)


def reload_config(config_path: str = None):
    """Reload configuration from file"""
    config.load_config(config_path)
