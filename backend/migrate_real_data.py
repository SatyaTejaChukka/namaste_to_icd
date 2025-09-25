"""
Migrate real CSV data to SQLite namaste_codes table
This uses your actual loaded CSV data files instead of sample data
"""

import os
import pandas as pd
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_csv_to_sqlite():
    """Load all your CSV data into the SQLite namaste_codes table"""
    
    from config import config
    
    DB_PATH = config.BASE_DIR / config.SQLITE_DB_NAME
    dbconnect_dir = config.DBCONNECT_DIR
    
    # Your CSV files mapping
    csv_files = {
        'ayurveda_clean_selected.csv': 'ayurveda',
        'siddha_clean_final.csv': 'siddha', 
        'unani_clean_final.csv': 'unani'
    }
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM namaste_codes")
        logger.info("Cleared existing data from namaste_codes")
        
        total_inserted = 0
        
        # Process each CSV file
        for csv_file, system in csv_files.items():
            file_path = os.path.join(dbconnect_dir, csv_file)
            
            if not os.path.exists(file_path):
                logger.warning(f"CSV file not found: {file_path}")
                continue
                
            logger.info(f"Loading {csv_file} for {system} system...")
            
            # Read CSV
            df = pd.read_csv(file_path)
            logger.info(f"Found {len(df)} rows in {csv_file}")
            logger.info(f"Columns: {list(df.columns)}")
            
            # Map columns based on system
            records = []
            
            if system == 'ayurveda':
                # ayurveda_clean_selected.csv columns
                for _, row in df.iterrows():
                    if pd.notna(row.get('NAMC_CODE')) and pd.notna(row.get('NAMC_term')):
                        records.append((
                            f"AYU-{str(row.get('NAMC_CODE', ''))}",  # Prefix with system
                            str(row.get('NAMC_term', '')),
                            str(row.get('NAMC__term_DEVANAGARI', '')),
                            str(row.get('short_definition', '') or row.get('long_definition', '') or 'Ayurveda terminology concept'),
                            system
                        ))
                        
            elif system == 'siddha':
                # siddha_clean_final.csv columns  
                for _, row in df.iterrows():
                    if pd.notna(row.get('NAMC_CODE')) and pd.notna(row.get('namc_term_word')):
                        records.append((
                            f"SID-{str(row.get('NAMC_CODE', ''))}",  # Prefix with system
                            str(row.get('namc_term_word', '')),
                            str(row.get('tamil_term', '')),
                            str(row.get('short_definition', '') or row.get('definition', '') or 'Siddha terminology concept'),
                            system
                        ))
                        
            elif system == 'unani':
                # unani_clean_final.csv columns
                for _, row in df.iterrows():
                    if pd.notna(row.get('numc_code')) and pd.notna(row.get('namc_term_word')):
                        records.append((
                            f"UNI-{str(row.get('numc_code', ''))}",  # Prefix with system
                            str(row.get('namc_term_word', '')),
                            str(row.get('arabic_term_word', '')),
                            str(row.get('short_definition_translation', '') or row.get('definition', '') or 'Unani terminology concept'),
                            system
                        ))
            
            # Insert records for this system
            if records:
                cursor.executemany(
                    "INSERT INTO namaste_codes (code, display, original_term, definition, system) VALUES (?, ?, ?, ?, ?)",
                    records
                )
                inserted_count = len(records)
                total_inserted += inserted_count
                logger.info(f"✅ Inserted {inserted_count} {system} terms")
            else:
                logger.warning(f"No valid records found in {csv_file}")
        
        # Commit all changes
        conn.commit()
        
        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM namaste_codes")
        final_count = cursor.fetchone()[0]
        logger.info(f"🎉 Migration completed! Total records: {final_count}")
        
        # Show distribution by system
        for system in ['ayurveda', 'siddha', 'unani']:
            cursor.execute("SELECT COUNT(*) FROM namaste_codes WHERE system = ?", (system,))
            count = cursor.fetchone()[0]
            logger.info(f"  {system.capitalize()}: {count} terms")
        
        # Show sample records
        cursor.execute("SELECT code, display, original_term, system FROM namaste_codes LIMIT 5")
        samples = cursor.fetchall()
        logger.info("Sample migrated data:")
        for code, display, original_term, system in samples:
            logger.info(f"  {code}: {display} | {original_term} ({system})")
        
        conn.close()
        logger.info("✅ Real data migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    migrate_csv_to_sqlite()