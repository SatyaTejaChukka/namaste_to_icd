"""
Create the namaste_codes table with proper schema
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_namaste_codes_table():
    """Create the namaste_codes table with proper schema"""
    
    from config import config
    DB_PATH = config.BASE_DIR / config.SQLITE_DB_NAME
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create the namaste_codes table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS namaste_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code VARCHAR(50) NOT NULL UNIQUE,
            display VARCHAR(255) NOT NULL,
            original_term VARCHAR(255),
            definition TEXT,
            system VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor.execute(create_table_sql)
        logger.info("Created namaste_codes table")
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_namaste_codes_code ON namaste_codes(code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_namaste_codes_system ON namaste_codes(system)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_namaste_codes_display ON namaste_codes(display)")
        
        logger.info("Created indexes on namaste_codes table")
        
        conn.commit()
        conn.close()
        
        logger.info("✅ namaste_codes table created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        raise

if __name__ == "__main__":
    create_namaste_codes_table()