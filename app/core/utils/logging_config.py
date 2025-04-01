"""
Logging configuration manager for the application.
"""
import logging
from PyQt5.QtCore import QSettings

class LoggingConfig:
    """Manager for application logging configuration."""
    
    # Map UI-friendly names to Python logging levels
    LOG_LEVELS = {
        "Debug": logging.DEBUG,
        "Info": logging.INFO,
        "Warning": logging.WARNING,
        "Error": logging.ERROR
    }
    
    @staticmethod
    def get_log_level():
        """Get the current log level from settings."""
        settings = QSettings("LiDoMa", "DockerManager")
        level_name = settings.value("logLevel", "Info")
        return LoggingConfig.LOG_LEVELS.get(level_name, logging.INFO)
    
    @staticmethod
    def set_log_level(level_name):
        """Set the log level based on the name."""
        if level_name not in LoggingConfig.LOG_LEVELS:
            logging.warning(f"Unknown log level: {level_name}, defaulting to Info")
            level_name = "Info"
        
        log_level = LoggingConfig.LOG_LEVELS[level_name]
        
        # Set the level for the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Update all handlers
        for handler in root_logger.handlers:
            handler.setLevel(log_level)
        
        logging.info(f"Log level set to: {level_name} ({log_level})")
        return log_level
    
    @staticmethod
    def apply_log_level_from_settings():
        """Apply the log level from current settings."""
        settings = QSettings("LiDoMa", "DockerManager")
        level_name = settings.value("logLevel", "Info")
        return LoggingConfig.set_log_level(level_name)
