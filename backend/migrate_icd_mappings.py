#!/usr/bin/env python3
"""
Migrate ICD-11 mapping data from CSV files to SQLite database.
Creates mapping tables and populates them with ICD-11 suggestions.
"""

import sqlite3
import pandas as pd
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_mapping_tables(conn):
    """Create ICD mapping tables with proper schema."""
    cursor = conn.cursor()
    
    # Create the mapping table for all systems
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS icd_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        namc_code TEXT NOT NULL,
        system TEXT NOT NULL,
        icd_code TEXT NOT NULL,
        icd_title TEXT NOT NULL,
        similarity_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (namc_code) REFERENCES namaste_codes(code)
    );
    """
    cursor.execute(create_table_sql)
    
    # Create index for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_namc_code ON icd_mappings(namc_code);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_system ON icd_mappings(system);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_icd_code ON icd_mappings(icd_code);")
    
    # Add native_term column to namaste_codes if it doesn't exist
    try:
        cursor.execute("ALTER TABLE namaste_codes ADD COLUMN native_term TEXT;")
        logger.info("Added native_term column to namaste_codes table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            logger.info("native_term column already exists in namaste_codes table")
        else:
            raise e
    
    conn.commit()
    logger.info("Created mapping tables and indexes")

def migrate_ayurveda_mappings(conn):
    """Migrate Ayurveda ICD mappings."""
    from config import config
    df = pd.read_csv(config.DBCONNECT_DIR / 'ayurveda_icd_mapping_suggestions.csv')
    logger.info(f"Loading {len(df)} Ayurveda ICD mappings...")
    
    cursor = conn.cursor()
    
    # Clear existing Ayurveda mappings
    cursor.execute("DELETE FROM icd_mappings WHERE system = 'ayurveda'")
    
    # Update namaste_codes with native terms
    for _, row in df.iterrows():
        namc_code = f"AYU-{row['NAMC_CODE']}"
        native_term = row['NATIVE_TERM']
        cursor.execute(
            "UPDATE namaste_codes SET native_term = ? WHERE code = ? AND system = 'ayurveda'",
            (native_term, namc_code)
        )
    
    # Insert mappings
    mappings_inserted = 0
    for _, row in df.iterrows():
        namc_code = f"AYU-{row['NAMC_CODE']}"
        
        # Check if the namc_code exists in namaste_codes
        cursor.execute("SELECT 1 FROM namaste_codes WHERE code = ? AND system = 'ayurveda'", (namc_code,))
        if cursor.fetchone():
            cursor.execute("""
                INSERT INTO icd_mappings (namc_code, system, icd_code, icd_title, similarity_score)
                VALUES (?, ?, ?, ?, ?)
            """, (namc_code, 'ayurveda', row['ICD_Code'], row['ICD_Title'], row['Similarity_Score']))
            mappings_inserted += 1
    
    conn.commit()
    logger.info(f"✅ Inserted {mappings_inserted} Ayurveda ICD mappings")

def migrate_siddha_mappings(conn):
    """Migrate Siddha ICD mappings."""
    from config import config
    df = pd.read_csv(config.DBCONNECT_DIR / 'siddha_icd_mapping_suggestions.csv')
    logger.info(f"Loading {len(df)} Siddha ICD mappings...")
    
    cursor = conn.cursor()
    
    # Clear existing Siddha mappings
    cursor.execute("DELETE FROM icd_mappings WHERE system = 'siddha'")
    
    # Update namaste_codes with native terms
    for _, row in df.iterrows():
        namc_code = f"SID-{row['NAMC_CODE']}"
        native_term = row['NATIVE_TERM']
        cursor.execute(
            "UPDATE namaste_codes SET native_term = ? WHERE code = ? AND system = 'siddha'",
            (native_term, namc_code)
        )
    
    # Insert mappings
    mappings_inserted = 0
    for _, row in df.iterrows():
        namc_code = f"SID-{row['NAMC_CODE']}"
        
        # Check if the namc_code exists in namaste_codes
        cursor.execute("SELECT 1 FROM namaste_codes WHERE code = ? AND system = 'siddha'", (namc_code,))
        if cursor.fetchone():
            cursor.execute("""
                INSERT INTO icd_mappings (namc_code, system, icd_code, icd_title, similarity_score)
                VALUES (?, ?, ?, ?, ?)
            """, (namc_code, 'siddha', row['ICD_Code'], row['ICD_Title'], row['Similarity_Score']))
            mappings_inserted += 1
    
    conn.commit()
    logger.info(f"✅ Inserted {mappings_inserted} Siddha ICD mappings")

def migrate_unani_mappings(conn):
    """Migrate Unani ICD mappings."""
    from config import config
    df = pd.read_csv(config.DBCONNECT_DIR / 'unani_icd_mapping_suggestions.csv')
    logger.info(f"Loading {len(df)} Unani ICD mappings...")
    
    cursor = conn.cursor()
    
    # Clear existing Unani mappings
    cursor.execute("DELETE FROM icd_mappings WHERE system = 'unani'")
    
    # Update namaste_codes with native terms
    for _, row in df.iterrows():
        namc_code = f"UNI-{row['NUMC_CODE']}"
        native_term = row['NATIVE_TERM']
        cursor.execute(
            "UPDATE namaste_codes SET native_term = ? WHERE code = ? AND system = 'unani'",
            (native_term, namc_code)
        )
    
    # Insert mappings
    mappings_inserted = 0
    for _, row in df.iterrows():
        namc_code = f"UNI-{row['NUMC_CODE']}"
        
        # Check if the namc_code exists in namaste_codes
        cursor.execute("SELECT 1 FROM namaste_codes WHERE code = ? AND system = 'unani'", (namc_code,))
        if cursor.fetchone():
            cursor.execute("""
                INSERT INTO icd_mappings (namc_code, system, icd_code, icd_title, similarity_score)
                VALUES (?, ?, ?, ?, ?)
            """, (namc_code, 'unani', row['ICD_Code'], row['ICD_Title'], row['Similarity_Score']))
            mappings_inserted += 1
    
    conn.commit()
    logger.info(f"✅ Inserted {mappings_inserted} Unani ICD mappings")

def main():
    """Main migration function."""
    logger.info("Starting ICD-11 mapping migration...")
    
    # Connect to database
    from config import config
    db_path = config.BASE_DIR / config.SQLITE_DB_NAME
    conn = sqlite3.connect(db_path)
    
    try:
        # Create mapping tables
        create_mapping_tables(conn)
        
        # Migrate all systems
        migrate_ayurveda_mappings(conn)
        migrate_siddha_mappings(conn)
        migrate_unani_mappings(conn)
        
        # Get final counts
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM icd_mappings")
        total_mappings = cursor.fetchone()[0]
        
        cursor.execute("SELECT system, COUNT(*) FROM icd_mappings GROUP BY system")
        system_counts = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM namaste_codes WHERE native_term IS NOT NULL")
        terms_with_native = cursor.fetchone()[0]
        
        logger.info("🎉 ICD-11 mapping migration completed!")
        logger.info(f"  Total mappings: {total_mappings}")
        logger.info(f"  Terms with native language: {terms_with_native}")
        for system, count in system_counts:
            logger.info(f"  {system.capitalize()}: {count} mappings")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()