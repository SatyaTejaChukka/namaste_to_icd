"""
Corrected data loader with proper column mappings
"""

import asyncio
import os
import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import logging

from config import config, FILES_AND_TABLES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use configuration from config module
DATABASE_URL = config.ASYNC_DATABASE_URL

async def create_tables_from_csv():
    """Create tables dynamically based on CSV structure"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dbconnect_dir = os.path.join(base_dir, 'Dbconnect')
    
    try:
        async with engine.begin() as conn:
            logger.info("Dropping all existing tables...")
            
            # Drop all existing tables
            for table_name in FILES_AND_TABLES.values():
                await conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
            
            logger.info("Creating tables based on CSV column structure...")
            
            # Create tables for each CSV
            for csv_file, table_name in FILES_AND_TABLES.items():
                file_path = os.path.join(dbconnect_dir, csv_file)
                
                if not os.path.exists(file_path):
                    logger.warning(f"CSV file not found: {file_path}")
                    continue
                
                # Read CSV to get column structure
                df = pd.read_csv(file_path, nrows=5)  # Just read a few rows to get structure
                
                # Normalize column names
                df.columns = df.columns.str.lower().str.replace(r'[^a-zA-Z0-9_]', '_', regex=True)
                
                # Generate CREATE TABLE statement
                columns = []
                columns.append("id SERIAL PRIMARY KEY")
                
                for col in df.columns:
                    # Determine data type based on sample values
                    sample_values = df[col].dropna()
                    if len(sample_values) > 0:
                        # Check if it looks like a number
                        if col.lower() in ['namc_id', 'numc_id', 'unnamed__0'] and not col.lower() in ['chapterno']:
                            columns.append(f"{col} INTEGER")
                        elif col.lower() in ['similarity_score']:
                            columns.append(f"{col} FLOAT")
                        else:
                            columns.append(f"{col} TEXT")
                    else:
                        columns.append(f"{col} TEXT")
                
                create_sql = f"CREATE TABLE {table_name} ({', '.join(columns)})"
                
                logger.info(f"Creating table {table_name} with columns: {df.columns.tolist()}")
                await conn.execute(text(create_sql))
            
            logger.info("All tables created successfully!")
            
    finally:
        await engine.dispose()

async def load_csv_data():
    """Load data from CSV files"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dbconnect_dir = os.path.join(base_dir, 'Dbconnect')
    
    try:
        async with async_session() as session:
            for csv_file, table_name in FILES_AND_TABLES.items():
                file_path = os.path.join(dbconnect_dir, csv_file)
                
                if not os.path.exists(file_path):
                    logger.warning(f"File not found: {file_path}")
                    continue
                
                logger.info(f"Loading {csv_file} into {table_name}...")
                
                # Read CSV
                df = pd.read_csv(file_path)
                logger.info(f"Found {len(df)} rows")
                
                # Normalize column names
                df.columns = df.columns.str.lower().str.replace(r'[^a-zA-Z0-9_]', '_', regex=True)
                
                # Handle NaN values - replace with None for database
                df = df.where(pd.notnull(df), None)
                
                # Convert to records
                records = df.to_dict('records')
                
                if records:
                    # Create dynamic insert statement
                    columns = list(df.columns)
                    placeholders = ', '.join([f':{col}' for col in columns])
                    columns_str = ', '.join(columns)
                    
                    insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                    
                    try:
                        # Insert in batches to avoid memory issues
                        batch_size = 1000
                        for i in range(0, len(records), batch_size):
                            batch = records[i:i+batch_size]
                            await session.execute(text(insert_sql), batch)
                            logger.info(f"Inserted batch {i//batch_size + 1}/{(len(records)-1)//batch_size + 1}")
                        
                        logger.info(f"✅ Successfully loaded {len(records)} records into {table_name}")
                    except Exception as e:
                        logger.error(f"❌ Error loading {csv_file}: {e}")
                        await session.rollback()
                        raise
            
            await session.commit()
            logger.info("🎉 All data committed successfully!")
            
    finally:
        await engine.dispose()

async def verify_data():
    """Verify the loaded data"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            logger.info("=== Data Verification ===")
            
            for table_name in FILES_AND_TABLES.values():
                try:
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.scalar()
                    logger.info(f"📊 {table_name}: {count} rows")
                except Exception as e:
                    logger.error(f"❌ Error checking {table_name}: {e}")
            
            # Test some specific queries
            logger.info("\n=== Sample Queries ===")
            
            # Test Ayurveda terms
            result = await session.execute(text("SELECT namc_code, namc_term FROM ayurveda_terms LIMIT 3"))
            rows = result.fetchall()
            logger.info(f"📋 Sample Ayurveda terms: {[(row.namc_code, row.namc_term) for row in rows]}")
            
            # Test Siddha terms
            result = await session.execute(text("SELECT namc_code, namc_term_word FROM siddha_terms LIMIT 3"))
            rows = result.fetchall()
            logger.info(f"📋 Sample Siddha terms: {[(row.namc_code, row.namc_term_word) for row in rows]}")
            
            # Test Unani terms
            result = await session.execute(text("SELECT numc_code, namc_term_word FROM unani_terms LIMIT 3"))
            rows = result.fetchall()
            logger.info(f"📋 Sample Unani terms: {[(row.numc_code, row.namc_term_word) for row in rows]}")
            
    finally:
        await engine.dispose()

async def main():
    """Main function"""
    logger.info("🚀 Starting corrected data loading process...")
    
    try:
        await create_tables_from_csv()
        await load_csv_data()
        await verify_data()
        logger.info("✅ Data loading completed successfully!")
    except Exception as e:
        logger.error(f"❌ Data loading failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())