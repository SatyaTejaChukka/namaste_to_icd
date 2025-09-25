import pandas as pd
from sqlalchemy import create_engine
import os
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import config, FILES_AND_TABLES

def load_csv_to_postgres(database_url, files_to_tables):
    """
    Loads data from a set of CSV files into specified PostgreSQL tables.

    Args:
        database_url (str): The connection string for the PostgreSQL database.
        files_to_tables (dict): A dictionary mapping CSV filenames to the desired
                                PostgreSQL table names.
    """
    try:
        # Create a SQLAlchemy engine to connect to the database
        engine = create_engine(database_url)
        # Test the connection
        with engine.connect() as connection:
            print("Successfully connected to the PostgreSQL database.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return

    # Get the directory containing CSV files
    csv_dir = Path(__file__).parent

    # Process each file
    for csv_file, table_name in files_to_tables.items():
        csv_path = csv_dir / csv_file
        if not csv_path.exists():
            print(f"--- Skipping '{csv_file}': File not found. ---")
            continue

        print(f"\n--- Processing '{csv_file}' ---")
        
        try:
            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(csv_path)
            print(f"Read {len(df)} rows from '{csv_file}'.")
            
            # Use pandas to_sql function to write the DataFrame to a SQL table
            # if_exists='replace': Drops and recreates the table.
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            
            print(f"Successfully loaded data into table '{table_name}'.")

        except Exception as e:
            print(f"An error occurred while processing '{csv_file}': {e}")
    
    print("\n--- All files processed. ---")

# Import configuration from config module
DATABASE_URL = config.DATABASE_URL
files_and_tables = FILES_AND_TABLES

# --- Execution ---
if __name__ == "__main__":
    print(f"Connecting to database: {config.DB_NAME} on {config.DB_HOST}")
    load_csv_to_postgres(DATABASE_URL, files_and_tables)

