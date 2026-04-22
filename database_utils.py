"""
Database utilities for patent pipeline.
Supports cloud storage download, Supabase PostgreSQL, and local SQLite.
"""

import os
import pandas as pd
from pathlib import Path
import psycopg2
import sqlite3
import requests
import sys

def download_database_if_needed():
    """Download database from cloud storage if DATABASE_URL is set and local file doesn't exist."""
    database_url = os.getenv("DATABASE_URL")
    db_path = Path("data/patent_pipeline.db")

    if database_url and not db_path.exists():
        print("📥 Downloading database from cloud storage...")
        try:
            # Create data directory
            db_path.parent.mkdir(parents=True, exist_ok=True)

            # Download database
            response = requests.get(database_url, stream=True, timeout=300)
            response.raise_for_status()

            with open(db_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"✅ Database downloaded successfully ({db_path.stat().st_size / (1024*1024):.1f} MB)")

        except Exception as e:
            print(f"❌ Failed to download database: {e}")
            raise

def get_database_connection():
    """
    Get database connection.
    Priority: Cloud storage download → Supabase → Local SQLite.
    """
    # First, check if we need to download from cloud storage
    download_database_if_needed()

    # Check for Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    db_password = os.getenv("SUPABASE_DB_PASSWORD")

    if supabase_url and db_password:
        try:
            # Use Supabase PostgreSQL connection with connection options
            project_ref = supabase_url.replace("https://", "").replace("http://", "").split(".")[0]
            conn_string = f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"

            # Add connection options to help with connectivity issues
            conn = psycopg2.connect(
                conn_string,
                connect_timeout=30,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5
            )
            return {"type": "supabase", "connection": conn}
        except Exception as e:
            print(f"⚠️  Supabase connection failed: {e}")
            print("Falling back to local SQLite...")
            # Fall through to SQLite

    # Use local SQLite (fallback)
    db_path = Path("data/patent_pipeline.db")
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found at {db_path}. "
            "For local development: Run patent_pipeline.py first. "
            "For Streamlit Cloud: Set DATABASE_URL to download from cloud storage."
        )
    conn = sqlite3.connect(str(db_path))
    return {"type": "sqlite", "connection": conn}

def execute_query(query: str, params=None) -> pd.DataFrame:
    """
    Execute SQL query and return results as DataFrame.
    """
    db = get_database_connection()

    if db["type"] == "supabase":
        # Use psycopg2
        cursor = db["connection"].cursor()
        cursor.execute(query, params or ())
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        results = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(results, columns=columns)
    else:
        # SQLite
        return pd.read_sql_query(query, db["connection"], params=params)