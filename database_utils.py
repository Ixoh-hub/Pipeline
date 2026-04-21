"""
Database utilities for patent pipeline.
Supports both local SQLite and Supabase PostgreSQL.
"""

import os
import pandas as pd
from pathlib import Path

def get_database_connection():
    """
    Get database connection.
    Uses Supabase if credentials are available, otherwise local SQLite.
    """
    # Check for Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if supabase_url and service_role_key:
        # Use Supabase PostgreSQL connection
        host = supabase_url.replace("https://", "").replace("http://", "").split(".")[0]
        conn_string = f"postgresql://postgres:{service_role_key}@db.{host}.supabase.co:5432/postgres"
        import psycopg2
        conn = psycopg2.connect(conn_string)
        return {"type": "supabase", "connection": conn}
    else:
        # Use local SQLite
        db_path = Path("data/patent_pipeline.db")
        if not db_path.exists():
            raise FileNotFoundError(f"Database not found at {db_path}. Run patent_pipeline.py first.")
        import sqlite3
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

            # But that's complex. Alternatively, use psycopg2 directly with Supabase connection string.

            # Supabase provides a PostgreSQL connection string.

            # Let's use that.

            import psycopg2
            conn_string = f"postgresql://postgres:{supabase_key}@{supabase_url.replace('https://', '').replace('http://', '')}/postgres"
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return pd.DataFrame(results, columns=columns)

        except Exception as e:
            raise Exception(f"Supabase query failed: {e}")

    else:
        # SQLite
        return pd.read_sql_query(query, db["connection"], params=params)