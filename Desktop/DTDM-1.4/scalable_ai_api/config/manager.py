"""
Configuration Manager for the Scalable AI API System.

Handles loading and validation of configuration from environment variables
and configuration files as specified in Requirements 9.1 and 9.5.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from scalable_ai_api.models import SystemConfiguration, ScalingPolicy


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass


class ConfigurationManager:
    """Manages system configuration loading and validation."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file
        self._config: Optional[SystemConfiguration] = None
    
    def load_configuration(self) -> SystemConfiguration:
        """Load and validate configuration from environment and files.
        
        Returns:
            SystemConfiguration: Validated system configuration
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            # Start with default configuration
            config_dict = self._get_default_config()
            
            # Override with file configuration if provided
            if self.config_file and Path(self.config_file).exists():
                file_config = self._load_config_file(self.config_file)
                config_dict.update(file_config)
            
            # Override with environment variables
            env_config = self._load_env_config()
            config_dict.update(env_config)
            
            # Create and validate configuration object
            self._config = self._create_system_config(config_dict)
            
            return self._config
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    def get_configuration(self) -> SystemConfiguration:
        """Get current configuration.
        
        Returns:
            SystemConfiguration: Current system configuration
            
        Raises:
            ConfigurationError: If configuration not loaded
        """
        if self._config is None:
            raise ConfigurationError("Configuration not loaded. Call load_configuration() first.")
        return self._config
    
    def validate_configuration(self, config: SystemConfiguration) -> bool:
        """Validate configuration parameters.
        
        Args:
            config: Configuration to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            # Validation is handled in the dataclass __post_init__ methods
            # Additional business logic validation can be added here
            
            # Validate scaling policy consistency
            policy = config.scaling_policy
            if policy.scale_up_threshold <= policy.scale_down_threshold:
                raise ConfigurationError(
                    f"Scale up threshold ({policy.scale_up_threshold}) must be greater than "
                    f"scale down threshold ({policy.scale_down_threshold})"
                )
            
            # Validate timeout relationships
            if config.health_check_timeout >= config.health_check_interval:
                raise ConfigurationError(
                    f"Health check timeout ({config.health_check_timeout}) must be less than "
                    f"health check interval ({config.health_check_interval})"
                )
            
            return True
            
        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {str(e)}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "load_balancer_port": 8000,
            "health_check_interval": 30,
            "health_check_timeout": 5,
            "request_timeout": 30,
            "max_retries": 3,
            "retry_backoff_factor": 2.0,
            "log_level": "INFO",
            "scaling_policy": {
                "min_instances": 2,
                "max_instances": 10,
                "scale_up_threshold": 80.0,
                "scale_down_threshold": 30.0,
                "cooldown_period": 300,
                "metrics_window": 300
            }
        }
    
    def _load_config_file(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Dict[str, Any]: Configuration dictionary
            
        Raises:
            ConfigurationError: If file cannot be loaded or parsed
        """
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.json'):
                    return json.load(f)
                elif config_file.endswith(('.yml', '.yaml')):
                    return yaml.safe_load(f)
                else:
                    raise ConfigurationError(f"Unsupported config file format: {config_file}")
                    
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {config_file}")
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ConfigurationError(f"Failed to parse configuration file: {str(e)}")
    
    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables.
        
        Returns:
            Dict[str, Any]: Configuration dictionary from environment
        """
        env_config = {}
        
        # Load basic configuration
        if os.getenv("LOAD_BALANCER_PORT"):
            env_config["load_balancer_port"] = int(os.getenv("LOAD_BALANCER_PORT"))
        
        if os.getenv("HEALTH_CHECK_INTERVAL"):
            env_config["health_check_interval"] = int(os.getenv("HEALTH_CHECK_INTERVAL"))
        
        if os.getenv("HEALTH_CHECK_TIMEOUT"):
            env_config["health_check_timeout"] = int(os.getenv("HEALTH_CHECK_TIMEOUT"))
        
        if os.getenv("REQUEST_TIMEOUT"):
            env_config["request_timeout"] = int(os.getenv("REQUEST_TIMEOUT"))
        
        if os.getenv("MAX_RETRIES"):
            env_config["max_retries"] = int(os.getenv("MAX_RETRIES"))
        
        if os.getenv("RETRY_BACKOFF_FACTOR"):
            env_config["retry_backoff_factor"] = float(os.getenv("RETRY_BACKOFF_FACTOR"))
        
        if os.getenv("LOG_LEVEL"):
            env_config["log_level"] = os.getenv("LOG_LEVEL")
        
        # Load scaling policy from environment
        scaling_policy = {}
        if os.getenv("MIN_INSTANCES"):
            scaling_policy["min_instances"] = int(os.getenv("MIN_INSTANCES"))
        
        if os.getenv("MAX_INSTANCES"):
            scaling_policy["max_instances"] = int(os.getenv("MAX_INSTANCES"))
        
        if os.getenv("SCALE_UP_THRESHOLD"):
            scaling_policy["scale_up_threshold"] = float(os.getenv("SCALE_UP_THRESHOLD"))
        
        if os.getenv("SCALE_DOWN_THRESHOLD"):
            scaling_policy["scale_down_threshold"] = float(os.getenv("SCALE_DOWN_THRESHOLD"))
        
        if os.getenv("COOLDOWN_PERIOD"):
            scaling_policy["cooldown_period"] = int(os.getenv("COOLDOWN_PERIOD"))
        
        if os.getenv("METRICS_WINDOW"):
            scaling_policy["metrics_window"] = int(os.getenv("METRICS_WINDOW"))
        
        if scaling_policy:
            env_config["scaling_policy"] = scaling_policy
        
        return env_config
    
    def _create_system_config(self, config_dict: Dict[str, Any]) -> SystemConfiguration:
        """Create SystemConfiguration object from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            SystemConfiguration: Validated configuration object
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            # Extract scaling policy if present
            scaling_policy_dict = config_dict.pop("scaling_policy", {})
            scaling_policy = ScalingPolicy(**scaling_policy_dict)
            
            # Create system configuration
            config = SystemConfiguration(
                scaling_policy=scaling_policy,
                **config_dict
            )
            
            # Validate the configuration
            self.validate_configuration(config)
            
            return config
            
        except TypeError as e:
            raise ConfigurationError(f"Invalid configuration parameters: {str(e)}")
        except ValueError as e:
            raise ConfigurationError(f"Invalid configuration values: {str(e)}")


def load_system_configuration(config_file: Optional[str] = None) -> SystemConfiguration:
    """Convenience function to load system configuration.
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        SystemConfiguration: Loaded and validated configuration
        
    Raises:
        ConfigurationError: If configuration loading fails
    """
    manager = ConfigurationManager(config_file)
    return manager.load_configuration()