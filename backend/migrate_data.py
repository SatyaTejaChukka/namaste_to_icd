"""
Data migration script to populate namaste_codes table from system-specific tables
"""

import asyncio
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_data():
    """Copy data from system-specific tables to namaste_codes table"""
    
    from config import config
    DB_PATH = config.BASE_DIR / config.SQLITE_DB_NAME
    
    try:
        # Use synchronous SQLite connection for direct operations
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Clear existing data in namaste_codes
        cursor.execute("DELETE FROM namaste_codes")
        logger.info("Cleared existing data from namaste_codes")
        
        # Insert data from ayurveda_terms
        logger.info("Migrating Ayurveda terms...")
        cursor.execute("""
            INSERT INTO namaste_codes (code, display, system)
            SELECT namc_code, namc_term, 'ayurveda'
            FROM ayurveda_terms
            WHERE namc_code IS NOT NULL AND namc_term IS NOT NULL
        """)
        ayurveda_count = cursor.rowcount
        logger.info(f"Migrated {ayurveda_count} Ayurveda terms")
        
        # Insert data from siddha_terms
        logger.info("Migrating Siddha terms...")
        cursor.execute("""
            INSERT INTO namaste_codes (code, display, system)
            SELECT namc_code, namc_term_word, 'siddha'
            FROM siddha_terms
            WHERE namc_code IS NOT NULL AND namc_term_word IS NOT NULL
        """)
        siddha_count = cursor.rowcount
        logger.info(f"Migrated {siddha_count} Siddha terms")
        
        # Insert data from unani_terms
        logger.info("Migrating Unani terms...")
        cursor.execute("""
            INSERT INTO namaste_codes (code, display, system)
            SELECT numc_code, namc_term_word, 'unani'
            FROM unani_terms
            WHERE numc_code IS NOT NULL AND namc_term_word IS NOT NULL
        """)
        unani_count = cursor.rowcount
        logger.info(f"Migrated {unani_count} Unani terms")
        
        # Commit the changes
        conn.commit()
        
        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM namaste_codes")
        total_count = cursor.fetchone()[0]
        logger.info(f"Total records in namaste_codes: {total_count}")
        
        # Show sample data
        cursor.execute("SELECT code, display, system FROM namaste_codes LIMIT 5")
        samples = cursor.fetchall()
        logger.info("Sample migrated data:")
        for code, display, system in samples:
            logger.info(f"  {system}: {code} - {display}")
        
        conn.close()
        logger.info("✅ Data migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(migrate_data())