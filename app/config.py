"""
Configuration Module
Centralized settings loaded from JSON configs in Documents
"""

import os
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (fallback for dev)
load_dotenv()

# Base paths - Consolidated under d8_data/
D8_DATA_PATH = Path(os.path.expanduser("~/Documents/d8_data"))
AGENTS_BASE_PATH = D8_DATA_PATH / "agentes"
WORKERS_BASE_PATH = D8_DATA_PATH / "workers"


@dataclass
class APIConfig:
    """API Keys and endpoints"""
    groq_api_key: str
    deepseek_base_url: str = "http://localhost:7100"
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
    groq_model: str = "llama-3.3-70b-versatile"


@dataclass
class MemoryConfig:
    """Vector database settings"""
    chroma_persist_directory: str = str(AGENTS_BASE_PATH / "memories/vector_store")
    chroma_collection_name: str = "agent_memory"


@dataclass
class LoggingConfig:
    """Logging settings"""
    log_level: str = "INFO"
    log_file: str = str(AGENTS_BASE_PATH / "logs/hive.log")


@dataclass
class CongressConfig:
    """Congress system settings"""
    # Supreme Council
    council_size: int = 7
    council_voting_threshold: float = 0.66  # Supermajority
    
    # Committee sizes
    niche_discovery_size: int = 7
    competitive_intelligence_size: int = 4
    technology_research_size: int = 3
    monetization_optimization_size: int = 3
    content_execution_size: int = 5
    operations_size: int = 3
    
    # Discovery settings
    discovery_frequency_hours: int = 6
    discovery_candidates_per_cycle: int = 10
    deep_analysis_batch_size: int = 3
    
    # Voting thresholds
    simple_majority_threshold: float = 0.51
    supermajority_threshold: float = 0.66
    qualified_majority_threshold: float = 0.75
    
    # API keys for data sources
    google_trends_api_key: Optional[str] = None
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None


@dataclass
class GeographicMarket:
    """Configuration for a geographic market"""
    code: str  # USA, ES, CL
    name: str
    language: str
    currency: str
    currency_symbol: str
    purchasing_power_index: float  # Relative to USA = 1.0
    digital_adoption_rate: float  # 0-1
    preferred_platforms: list
    payment_methods: list
    business_hours_offset: int  # UTC offset


@dataclass
class MarketingConfig:
    """Marketing and geographic targeting settings"""
    target_markets: Dict[str, GeographicMarket] = None
    primary_market: str = "USA"
    
    def __post_init__(self):
        if self.target_markets is None:
            self.target_markets = {
                "USA": GeographicMarket(
                    code="USA",
                    name="United States",
                    language="English",
                    currency="USD",
                    currency_symbol="$",
                    purchasing_power_index=1.0,
                    digital_adoption_rate=0.92,
                    preferred_platforms=["Instagram", "TikTok", "YouTube", "Twitter", "LinkedIn"],
                    payment_methods=["Stripe", "PayPal", "Credit Card", "Apple Pay", "Google Pay"],
                    business_hours_offset=-5  # EST
                ),
                "ES": GeographicMarket(
                    code="ES",
                    name="España",
                    language="Spanish",
                    currency="EUR",
                    currency_symbol="€",
                    purchasing_power_index=0.75,
                    digital_adoption_rate=0.88,
                    preferred_platforms=["Instagram", "YouTube", "TikTok", "Twitter", "LinkedIn"],
                    payment_methods=["Stripe", "PayPal", "Bizum", "Credit Card"],
                    business_hours_offset=+1  # CET
                ),
                "CL": GeographicMarket(
                    code="CL",
                    name="Chile",
                    language="Spanish",
                    currency="CLP",
                    currency_symbol="$",
                    purchasing_power_index=0.45,
                    digital_adoption_rate=0.82,
                    preferred_platforms=["Instagram", "TikTok", "YouTube", "Twitter", "LinkedIn"],
                    payment_methods=["MercadoPago", "WebPay", "Flow", "PayPal", "Credit Card"],
                    business_hours_offset=-3  # CLT
                )
            }


@dataclass
class FlaskConfig:
    """Flask server settings"""
    flask_env: str = "development"
    flask_debug: bool = True
    flask_port: int = 7001


class Config:
    """Main configuration object"""
    
    def __init__(self):
        # Load JSON configs
        self._load_agent_config()
        self._load_worker_config()
        
        # API Configuration (prioritize JSON, fallback to .env)
        groq_key = self._agent_config.get("api", {}).get("groq_api_key") or os.getenv("GROQ_API_KEY")
        if not groq_key:
            raise ValueError("GROQ_API_KEY not found in agent config or .env")
            
        self.api = APIConfig(
            groq_api_key=groq_key,
            deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "http://localhost:7100"),
            deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-coder:33b")
        )
        
        # Evolution Configuration
        evo = self._agent_config.get("evolution", {})
        self.evolution = EvolutionConfig(
            population_size=evo.get("population_size", 20),
            mutation_rate=evo.get("mutation_rate", 0.1),
            crossover_rate=evo.get("crossover_rate", 0.7),
            generations=evo.get("generations", 100),
            elite_size=evo.get("elite_size", 2),
            fitness_evaluation_interval=self._agent_config.get("agent_limits", {}).get("fitness_evaluation_interval", 86400)
        )
        
        # Agent Configuration
        limits = self._agent_config.get("agent_limits", {})
        self.agent = AgentConfig(
            max_actions_per_day=limits.get("max_actions_per_day", 1000),
            action_cooldown_seconds=limits.get("action_cooldown_seconds", 60),
            groq_model=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
        )
        
        # Memory Configuration
        mem = self._agent_config.get("memory", {})
        self.memory = MemoryConfig(
            chroma_persist_directory=str(AGENTS_BASE_PATH / mem.get("vector_store_path", "memories/vector_store")),
            chroma_collection_name=mem.get("chroma_collection_name", "agent_memory")
        )
        
        # Logging Configuration
        log = self._agent_config.get("logging", {})
        self.logging = LoggingConfig(
            log_level=log.get("level", "INFO"),
            log_file=str(AGENTS_BASE_PATH / log.get("path", "logs") / "hive.log")
        )
        
        # Flask Configuration
        self.flask = FlaskConfig(
            flask_env=os.getenv("FLASK_ENV", "development"),
            flask_debug=os.getenv("FLASK_DEBUG", "True").lower() == "true",
            flask_port=int(os.getenv("FLASK_PORT", 7001))
        )
        
        # Congress Configuration
        self.congress = CongressConfig(
            council_size=int(os.getenv("COUNCIL_SIZE", 7)),
            council_voting_threshold=float(os.getenv("COUNCIL_VOTING_THRESHOLD", 0.66)),
            niche_discovery_size=int(os.getenv("NICHE_DISCOVERY_SIZE", 7)),
            competitive_intelligence_size=int(os.getenv("COMPETITIVE_INTELLIGENCE_SIZE", 4)),
            technology_research_size=int(os.getenv("TECHNOLOGY_RESEARCH_SIZE", 3)),
            monetization_optimization_size=int(os.getenv("MONETIZATION_OPTIMIZATION_SIZE", 3)),
            content_execution_size=int(os.getenv("CONTENT_EXECUTION_SIZE", 5)),
            operations_size=int(os.getenv("OPERATIONS_SIZE", 3)),
            discovery_frequency_hours=int(os.getenv("DISCOVERY_FREQUENCY_HOURS", 6)),
            discovery_candidates_per_cycle=int(os.getenv("DISCOVERY_CANDIDATES_PER_CYCLE", 10)),
            deep_analysis_batch_size=int(os.getenv("DEEP_ANALYSIS_BATCH_SIZE", 3)),
            google_trends_api_key=os.getenv("GOOGLE_TRENDS_API_KEY"),
            reddit_client_id=os.getenv("REDDIT_CLIENT_ID"),
            reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET")
        )
        
        # Marketing Configuration
        self.marketing = MarketingConfig(
            primary_market=os.getenv("PRIMARY_MARKET", "USA")
        )
    
    def _load_agent_config(self) -> None:
        """Load agent configuration from JSON"""
        config_path = AGENTS_BASE_PATH / "config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                self._agent_config = json.load(f)
        else:
            print(f"⚠️  Agent config not found at {config_path}, using defaults")
            self._agent_config = {}
    
    def _load_worker_config(self) -> None:
        """Load worker configuration from JSON"""
        config_path = WORKERS_BASE_PATH / "config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                self._worker_config = json.load(f)
        else:
            print(f"⚠️  Worker config not found at {config_path}, using defaults")
            self._worker_config = {}
    
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
