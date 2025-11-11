"""
Configuration management module for the AI Mock Interview Platform.

This module loads configuration from config.yaml and environment variables,
validates required values, and provides a centralized configuration object.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from src.exceptions import ConfigurationError


@dataclass
class AIProviderConfig:
    """Configuration for an AI provider."""
    default_model: str
    temperature: float
    max_tokens: int
    api_key: Optional[str] = None


@dataclass
class StorageConfig:
    """Configuration for file storage."""
    data_dir: str
    sessions_dir: str
    logs_dir: str
    max_file_size_mb: int


@dataclass
class AudioConfig:
    """Configuration for audio communication."""
    sample_rate: int
    channels: int
    format: str


@dataclass
class VideoConfig:
    """Configuration for video communication."""
    fps: int
    resolution: str
    format: str


@dataclass
class WhiteboardConfig:
    """Configuration for whiteboard canvas."""
    canvas_width: int
    canvas_height: int
    stroke_width: int


@dataclass
class ScreenShareConfig:
    """Configuration for screen sharing."""
    fps: int
    format: str


@dataclass
class CommunicationConfig:
    """Configuration for all communication modes."""
    audio: AudioConfig
    video: VideoConfig
    whiteboard: WhiteboardConfig
    screen_share: ScreenShareConfig


@dataclass
class SessionConfig:
    """Configuration for interview sessions."""
    default_duration_minutes: int
    max_duration_minutes: int
    auto_save_interval_seconds: int


@dataclass
class LoggingConfig:
    """Configuration for logging system."""
    level: str
    format: str
    console_output: bool
    file_output: bool
    database_output: bool
    max_file_size_mb: int
    backup_count: int


@dataclass
class TokenTrackingConfig:
    """Configuration for token tracking."""
    enabled: bool
    track_by_operation: bool
    display_costs: bool


@dataclass
class DatabaseConfig:
    """Configuration for database connection."""
    host: str
    port: int
    database: str
    user: str
    password: str
    pool_size: int
    max_overflow: int
    pool_timeout: int
    pool_recycle: int


@dataclass
class Config:
    """
    Main configuration object for the application.
    
    Attributes:
        ai_providers: AI provider configurations
        storage: Storage configuration
        communication: Communication modes configuration
        session: Session configuration
        logging: Logging configuration
        token_tracking: Token tracking configuration
        database: Database configuration
    """
    ai_providers: Dict[str, AIProviderConfig]
    storage: StorageConfig
    communication: CommunicationConfig
    session: SessionConfig
    logging: LoggingConfig
    token_tracking: TokenTrackingConfig
    database: DatabaseConfig


def load_config(config_path: str = "config.yaml") -> Config:
    """
    Load configuration from YAML file and environment variables.
    
    Args:
        config_path: Path to configuration YAML file
        
    Returns:
        Config object with all configuration values
        
    Raises:
        ConfigurationError: If configuration is invalid or missing required values
    """
    # Load YAML configuration
    try:
        with open(config_path, "r") as f:
            yaml_config = yaml.safe_load(f)
    except FileNotFoundError:
        raise ConfigurationError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in configuration file: {e}")

    # Load environment variables
    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_PORT": os.getenv("DB_PORT", "5432"),
        "DB_NAME": os.getenv("DB_NAME", "interview_platform"),
        "DB_USER": os.getenv("DB_USER", "interview_user"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DATA_DIR": os.getenv("DATA_DIR", "./data"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    }

    # Validate required environment variables
    required_env_vars = ["DB_PASSWORD"]
    missing_vars = [var for var in required_env_vars if not env_vars.get(var)]
    if missing_vars:
        raise ConfigurationError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    # Validate at least one AI provider API key is present
    if not env_vars.get("OPENAI_API_KEY") and not env_vars.get("ANTHROPIC_API_KEY"):
        raise ConfigurationError(
            "At least one AI provider API key must be set (OPENAI_API_KEY or ANTHROPIC_API_KEY)"
        )

    try:
        # Build AI provider configurations
        ai_providers = {}
        for provider_name, provider_config in yaml_config.get("ai_providers", {}).items():
            api_key = None
            if provider_name == "openai":
                api_key = env_vars.get("OPENAI_API_KEY")
            elif provider_name == "anthropic":
                api_key = env_vars.get("ANTHROPIC_API_KEY")

            ai_providers[provider_name] = AIProviderConfig(
                default_model=provider_config["default_model"],
                temperature=provider_config["temperature"],
                max_tokens=provider_config["max_tokens"],
                api_key=api_key,
            )

        # Build storage configuration
        storage_config = yaml_config.get("storage", {})
        data_dir = env_vars.get("DATA_DIR", storage_config.get("data_dir", "./data"))
        storage = StorageConfig(
            data_dir=data_dir,
            sessions_dir=storage_config.get("sessions_dir", f"{data_dir}/sessions"),
            logs_dir=storage_config.get("logs_dir", "./logs"),
            max_file_size_mb=storage_config.get("max_file_size_mb", 100),
        )

        # Build communication configuration
        comm_config = yaml_config.get("communication", {})
        audio_config = comm_config.get("audio", {})
        video_config = comm_config.get("video", {})
        whiteboard_config = comm_config.get("whiteboard", {})
        screen_config = comm_config.get("screen_share", {})

        communication = CommunicationConfig(
            audio=AudioConfig(
                sample_rate=audio_config.get("sample_rate", 16000),
                channels=audio_config.get("channels", 1),
                format=audio_config.get("format", "wav"),
            ),
            video=VideoConfig(
                fps=video_config.get("fps", 30),
                resolution=video_config.get("resolution", "1280x720"),
                format=video_config.get("format", "webm"),
            ),
            whiteboard=WhiteboardConfig(
                canvas_width=whiteboard_config.get("canvas_width", 800),
                canvas_height=whiteboard_config.get("canvas_height", 600),
                stroke_width=whiteboard_config.get("stroke_width", 2),
            ),
            screen_share=ScreenShareConfig(
                fps=screen_config.get("fps", 10),
                format=screen_config.get("format", "png"),
            ),
        )

        # Build session configuration
        session_config = yaml_config.get("session", {})
        session = SessionConfig(
            default_duration_minutes=session_config.get("default_duration_minutes", 45),
            max_duration_minutes=session_config.get("max_duration_minutes", 90),
            auto_save_interval_seconds=session_config.get("auto_save_interval_seconds", 60),
        )

        # Build logging configuration
        logging_config = yaml_config.get("logging", {})
        log_level = env_vars.get("LOG_LEVEL", logging_config.get("level", "INFO"))
        logging = LoggingConfig(
            level=log_level,
            format=logging_config.get("format", "json"),
            console_output=logging_config.get("console_output", True),
            file_output=logging_config.get("file_output", True),
            database_output=logging_config.get("database_output", True),
            max_file_size_mb=logging_config.get("max_file_size_mb", 10),
            backup_count=logging_config.get("backup_count", 5),
        )

        # Build token tracking configuration
        token_config = yaml_config.get("token_tracking", {})
        token_tracking = TokenTrackingConfig(
            enabled=token_config.get("enabled", True),
            track_by_operation=token_config.get("track_by_operation", True),
            display_costs=token_config.get("display_costs", True),
        )

        # Build database configuration
        db_config = yaml_config.get("database", {})
        database = DatabaseConfig(
            host=env_vars["DB_HOST"],
            port=int(env_vars["DB_PORT"]),
            database=env_vars["DB_NAME"],
            user=env_vars["DB_USER"],
            password=env_vars["DB_PASSWORD"],
            pool_size=db_config.get("pool_size", 5),
            max_overflow=db_config.get("max_overflow", 10),
            pool_timeout=db_config.get("pool_timeout", 30),
            pool_recycle=db_config.get("pool_recycle", 3600),
        )

        # Create and return main config object
        return Config(
            ai_providers=ai_providers,
            storage=storage,
            communication=communication,
            session=session,
            logging=logging,
            token_tracking=token_tracking,
            database=database,
        )

    except KeyError as e:
        raise ConfigurationError(f"Missing required configuration key: {e}")
    except (ValueError, TypeError) as e:
        raise ConfigurationError(f"Invalid configuration value: {e}")


def validate_config(config: Config) -> None:
    """
    Validate configuration values.
    
    Args:
        config: Configuration object to validate
        
    Raises:
        ConfigurationError: If configuration values are invalid
    """
    # Validate AI provider configurations
    for provider_name, provider_config in config.ai_providers.items():
        if provider_config.temperature < 0 or provider_config.temperature > 2:
            raise ConfigurationError(
                f"Invalid temperature for {provider_name}: {provider_config.temperature}. "
                "Must be between 0 and 2."
            )
        if provider_config.max_tokens <= 0:
            raise ConfigurationError(
                f"Invalid max_tokens for {provider_name}: {provider_config.max_tokens}. "
                "Must be positive."
            )

    # Validate storage paths exist or can be created
    for path_attr in ["data_dir", "sessions_dir", "logs_dir"]:
        path = getattr(config.storage, path_attr)
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ConfigurationError(f"Cannot create directory {path}: {e}")

    # Validate session configuration
    if config.session.default_duration_minutes <= 0:
        raise ConfigurationError(
            f"Invalid default_duration_minutes: {config.session.default_duration_minutes}. "
            "Must be positive."
        )
    if config.session.max_duration_minutes < config.session.default_duration_minutes:
        raise ConfigurationError(
            f"max_duration_minutes ({config.session.max_duration_minutes}) must be >= "
            f"default_duration_minutes ({config.session.default_duration_minutes})"
        )

    # Validate logging configuration
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if config.logging.level not in valid_log_levels:
        raise ConfigurationError(
            f"Invalid log level: {config.logging.level}. "
            f"Must be one of {', '.join(valid_log_levels)}"
        )

    # Validate database configuration
    if config.database.pool_size <= 0:
        raise ConfigurationError(
            f"Invalid pool_size: {config.database.pool_size}. Must be positive."
        )
    if config.database.max_overflow < 0:
        raise ConfigurationError(
            f"Invalid max_overflow: {config.database.max_overflow}. Must be non-negative."
        )


def get_config(config_path: str = "config.yaml") -> Config:
    """
    Load and validate configuration.
    
    Args:
        config_path: Path to configuration YAML file
        
    Returns:
        Validated Config object
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    config = load_config(config_path)
    validate_config(config)
    return config
