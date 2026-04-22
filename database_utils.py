"""
Database utilities for patent pipeline.
Supports both local SQLite and Supabase PostgreSQL.
"""

import os
import pandas as pd
from pathlib import Path
import psycopg2
import sqlite3

def get_database_connection():
    """
    Get database connection.
    Uses Supabase if credentials are available, otherwise local SQLite.
    """
    # Check for Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    db_password = os.getenv("SUPABASE_DB_PASSWORD")

    if supabase_url and db_password:
        # Use Supabase PostgreSQL connection
        # Extract project ref from URL
        project_ref = supabase_url.replace("https://", "").replace("http://", "").split(".")[0]
        conn_string = f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"
        conn = psycopg2.connect(conn_string)
        return {"type": "supabase", "connection": conn}
    else:
        # Use local SQLite
        db_path = Path("data/patent_pipeline.db")
        if not db_path.exists():
            raise FileNotFoundError(f"Database not found at {db_path}. Run patent_pipeline.py first.")
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