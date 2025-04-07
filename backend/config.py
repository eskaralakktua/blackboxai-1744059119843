import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Settings:
    # Configuración de la API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Wallet Analysis API"
    
    # Claves de API
    MORALIS_API_KEY: str = os.getenv("MORALIS_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Configuración de blockchain
    SUPPORTED_CHAINS = {
        "ethereum": {
            "name": "Ethereum Mainnet",
            "chain_id": 1,
            "rpc_url": os.getenv("ETH_RPC_URL", "https://eth-mainnet.g.alchemy.com/v2/your-api-key")
        },
        "bsc": {
            "name": "BNB Smart Chain",
            "chain_id": 56,
            "rpc_url": os.getenv("BSC_RPC_URL", "https://bsc-dataseed.binance.org/")
        },
        "polygon": {
            "name": "Polygon Mainnet",
            "chain_id": 137,
            "rpc_url": os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com")
        }
    }
    
    # Configuración de análisis
    MAX_WALLETS_PER_REQUEST: int = 100
    MAX_TRANSACTIONS_PER_WALLET: int = 1000
    ANALYSIS_TIMEFRAME_DAYS: int = 30
    
    # Configuración de reportes
    REPORT_TEMP_DIR: str = "temp_reports"
    PDF_TEMPLATE_PATH: str = "templates/report_template.html"
    
    # Configuración de OpenAI
    GPT_MODEL: str = "gpt-4"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7

    class Config:
        case_sensitive = True

settings = Settings()