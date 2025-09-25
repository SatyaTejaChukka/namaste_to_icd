"""
Configuration management for AYUSH Terminology Service
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import urllib.parse

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Application configuration"""
    
    # Database Configuration
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = urllib.parse.quote_plus(os.getenv('DB_PASSWORD', ''))
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'hackathon_db')
    
    # SQLite Database (fallback)
    SQLITE_DB_NAME = os.getenv('SQLITE_DB_NAME', 'namaste_terminology.db')
    
    # Server Configuration
    SERVER_HOST = os.getenv('SERVER_HOST', '127.0.0.1')
    SERVER_PORT = int(os.getenv('SERVER_PORT', '8000'))
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '8000'))
    
    # Constructed URLs
    @property
    def DATABASE_URL(self):
        """PostgreSQL database URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def ASYNC_DATABASE_URL(self):
        """Async PostgreSQL database URL"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def SQLITE_URL(self):
        """SQLite database URL"""
        db_path = Path(__file__).parent / self.SQLITE_DB_NAME
        return f"sqlite+aiosqlite:///{db_path}"
    
    # File paths
    @property
    def BASE_DIR(self):
        """Base directory of the project"""
        return Path(__file__).parent
    
    @property
    def DBCONNECT_DIR(self):
        """Directory containing CSV data files"""
        return self.BASE_DIR / 'Dbconnect'

# Create a global config instance
config = Config()

# CSV file mappings
FILES_AND_TABLES = {
    'ayurveda_clean_selected.csv': 'ayurveda_terms',
    'ayurveda_icd_mapping_suggestions.csv': 'ayurveda_icd_mappings',
    'icd11_final_clean.csv': 'icd11_codes',
    'siddha_clean_final.csv': 'siddha_terms',
    'siddha_icd_mapping_suggestions.csv': 'siddha_icd_mappings',
    'unani_clean_final.csv': 'unani_terms',
    'unani_icd_mapping_suggestions.csv': 'unani_icd_mappings'
}
