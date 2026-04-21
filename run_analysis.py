#!/usr/bin/env python3
"""Run analysis queries on the existing patent database."""

import sqlite3
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path.cwd()
DATA_DIR = ROOT_DIR / "data"
REPORTS_DIR = ROOT_DIR / "reports"
DB_PATH = DATA_DIR / "patent_pipeline.db"

def run_analysis():
    print(f"[{datetime.now()}] Connecting to database...")
    conn = sqlite3.connect(DB_PATH, timeout=300)  # 5 minute timeout
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA journal_mode = WAL")
    
    print(f"[{datetime.now()}] Creating indexes...")
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_patent ON relationships(patent_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_inventor ON relationships(inventor_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_company ON relationships(company_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patents_year ON patents(year)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventors_country ON inventors(country)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventors_name ON inventors(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name)")
    conn.commit()
    print(f"[{datetime.now()}] Indexes created")
    
    # Check data
    cursor.execute("SELECT COUNT(*) FROM patents")
    patent_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM inventors")
    inventor_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM companies")
    company_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM relationships")
    relationship_count = cursor.fetchone()[0]
    
    print(f"[{datetime.now()}] Database stats:")
    print(f"  Patents: {patent_count}")
    print(f"  Inventors: {inventor_count}")
    print(f"  Companies: {company_count}")
    print(f"  Relationships: {relationship_count}")
    
    queries = {
        "top_inventors": (
            "SELECT i.name, stats.patents "
            "FROM inventors i "
            "JOIN (SELECT inventor_id, COUNT(DISTINCT patent_id) AS patents "
            "      FROM relationships GROUP BY inventor_id) stats "
            "ON i.inventor_id = stats.inventor_id "
            "ORDER BY stats.patents DESC, i.name LIMIT 10"
        ),
        "top_companies": (
            "SELECT c.name, stats.patents "
            "FROM companies c "
            "JOIN (SELECT company_id, COUNT(DISTINCT patent_id) AS patents "
            "      FROM relationships GROUP BY company_id) stats "
            "ON c.company_id = stats.company_id "
            "ORDER BY stats.patents DESC, c.name LIMIT 10"
        ),
        "top_countries": (
            "SELECT i.country AS country, COUNT(DISTINCT r.patent_id) AS patents "
            "FROM inventors i "
            "JOIN relationships r ON i.inventor_id = r.inventor_id "
            "WHERE i.country IS NOT NULL AND i.country != '' "
            "GROUP BY i.country ORDER BY patents DESC, i.country LIMIT 10"
        ),
        "country_trends": (
            "SELECT p.year, COUNT(*) AS patents "
            "FROM patents p GROUP BY p.year ORDER BY p.year"
        ),
    }
    
    results = {}
    for name, sql in queries.items():
        print(f"[{datetime.now()}] Running query: {name}...")
        results[name] = pd.read_sql_query(sql, conn)
        print(f"[{datetime.now()}]   {name}: {len(results[name])} rows")
    
    print(f"[{datetime.now()}] Writing CSV reports...")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    results["top_inventors"].to_csv(REPORTS_DIR / "top_inventors.csv", index=False)
    results["top_companies"].to_csv(REPORTS_DIR / "top_companies.csv", index=False)
    results["top_countries"].to_csv(REPORTS_DIR / "top_countries.csv", index=False)
    results["country_trends"].to_csv(REPORTS_DIR / "country_trends.csv", index=False)
    
    print(f"[{datetime.now()}] Writing JSON report...")
    report = {
        "total_patents": patent_count,
        "top_inventors": results["top_inventors"].to_dict(orient="records"),
        "top_companies": results["top_companies"].to_dict(orient="records"),
        "top_countries": results["top_countries"].to_dict(orient="records"),
        "country_trends": results["country_trends"].to_dict(orient="records"),
    }
    
    with open(REPORTS_DIR / "patent_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    print(f"[{datetime.now()}] Printing console report...")
    top_inventors = results["top_inventors"].head(3)
    top_companies = results["top_companies"].head(3)
    top_countries = results["top_countries"].head(3)
    
    print("\n================== PATENT REPORT ===================")
    print(f"Total Patents: {patent_count:,}")
    print("Top Inventors: " + ", ".join([f"{i+1}. {row['name']} - {row['patents']}" for i, (_, row) in enumerate(top_inventors.iterrows())]))
    print("Top Companies: " + ", ".join([f"{i+1}. {row['name']} - {row['patents']}" for i, (_, row) in enumerate(top_companies.iterrows())]))
    print("Top Countries: " + ", ".join([f"{i+1}. {row['country']} - {row['patents']}" for i, (_, row) in enumerate(top_countries.iterrows())]))
    print("====================================================\n")
    
    conn.close()
    print(f"[{datetime.now()}] Analysis complete!")

if __name__ == "__main__":
    try:
        run_analysis()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
