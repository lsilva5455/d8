"""
Configuration Module
Centralized settings loaded from environment variables
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class APIConfig:
    """API Keys and endpoints"""
    groq_api_key: str
    deepseek_base_url: str = "http://localhost:11434"
    deepseek_model: str = "deepseek-coder:33b"


@dataclass
class EvolutionConfig:
    """Genetic algorithm parameters"""
    population_size: int = 20
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    generations: int = 100
    elite_size: int = 2
    fitness_evaluation_interval: int = 86400  # 24 hours


@dataclass
class AgentConfig:
    """Agent behavior settings"""
    max_actions_per_day: int = 1000
    action_cooldown_seconds: int = 60
    groq_model: str = "mixtral-8x7b-32768"


@dataclass
class MemoryConfig:
    """Vector database settings"""
    chroma_persist_directory: str = "./data/chroma_db"
    chroma_collection_name: str = "agent_memory"


@dataclass
class ContentEmpireConfig:
    """Content generation settings"""
    wordpress_url: Optional[str] = None
    wordpress_username: Optional[str] = None
    wordpress_password: Optional[str] = None


@dataclass
class DeviceFarmConfig:
    """Device automation settings"""
    appium_server_url: str = "http://localhost:4723"
    android_devices: list = None


@dataclass
class LoggingConfig:
    """Logging settings"""
    log_level: str = "INFO"
    log_file: str = "./data/logs/hive.log"


@dataclass
class FlaskConfig:
    """Flask server settings"""
    flask_env: str = "development"
    flask_debug: bool = True
    flask_port: int = 5000


class Config:
    """Main configuration object"""
    
    def __init__(self):
        # API Configuration
        self.api = APIConfig(
            groq_api_key=self._get_required_env("GROQ_API_KEY"),
            deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "http://localhost:11434"),
            deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-coder:33b")
        )
        
        # Evolution Configuration
        self.evolution = EvolutionConfig(
            population_size=int(os.getenv("POPULATION_SIZE", 20)),
            mutation_rate=float(os.getenv("MUTATION_RATE", 0.1)),
            crossover_rate=float(os.getenv("CROSSOVER_RATE", 0.7)),
            generations=int(os.getenv("GENERATIONS", 100)),
            elite_size=int(os.getenv("ELITE_SIZE", 2)),
            fitness_evaluation_interval=int(os.getenv("FITNESS_EVALUATION_INTERVAL", 86400))
        )
        
        # Agent Configuration
        self.agent = AgentConfig(
            max_actions_per_day=int(os.getenv("MAX_ACTIONS_PER_DAY", 1000)),
            action_cooldown_seconds=int(os.getenv("ACTION_COOLDOWN_SECONDS", 60)),
            groq_model=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
        )
        
        # Memory Configuration
        self.memory = MemoryConfig(
            chroma_persist_directory=os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db"),
            chroma_collection_name=os.getenv("CHROMA_COLLECTION_NAME", "agent_memory")
        )
        
        # Content Empire Configuration
        self.content_empire = ContentEmpireConfig(
            wordpress_url=os.getenv("WORDPRESS_URL"),
            wordpress_username=os.getenv("WORDPRESS_USERNAME"),
            wordpress_password=os.getenv("WORDPRESS_PASSWORD")
        )
        
        # Device Farm Configuration
        android_devices_str = os.getenv("ANDROID_DEVICES", "")
        self.device_farm = DeviceFarmConfig(
            appium_server_url=os.getenv("APPIUM_SERVER_URL", "http://localhost:4723"),
            android_devices=android_devices_str.split(",") if android_devices_str else []
        )
        
        # Logging Configuration
        self.logging = LoggingConfig(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "./data/logs/hive.log")
        )
        
        # Flask Configuration
        self.flask = FlaskConfig(
            flask_env=os.getenv("FLASK_ENV", "development"),
            flask_debug=os.getenv("FLASK_DEBUG", "True").lower() == "true",
            flask_port=int(os.getenv("FLASK_PORT", 5000))
        )
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error"""
        value = os.getenv(key)
        if not value:
            raise ValueError(
                f"Required environment variable {key} is not set. "
                f"Please check your .env file."
            )
        return value
    
    def validate(self) -> None:
        """Validate configuration"""
        # Check required API keys
        if not self.api.groq_api_key:
            raise ValueError("GROQ_API_KEY is required")
        
        # Validate numeric ranges
        if not 0 <= self.evolution.mutation_rate <= 1:
            raise ValueError("MUTATION_RATE must be between 0 and 1")
        
        if not 0 <= self.evolution.crossover_rate <= 1:
            raise ValueError("CROSSOVER_RATE must be between 0 and 1")
        
        print("✅ Configuration validated successfully")


# Global config instance
config = Config()


if __name__ == "__main__":
    # Test configuration
    print("🔧 Testing configuration...")
    try:
        config.validate()
        print("\n📋 Configuration Summary:")
        print(f"  Evolution: {config.evolution.population_size} agents, {config.evolution.generations} generations")
        print(f"  Mutation Rate: {config.evolution.mutation_rate}")
        print(f"  Crossover Rate: {config.evolution.crossover_rate}")
        print(f"  DeepSeek: {config.api.deepseek_base_url}")
        print(f"  Flask: Port {config.flask.flask_port}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
