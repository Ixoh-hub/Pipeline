#!/usr/bin/env python3
"""Create data visualizations for patent analysis."""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

ROOT_DIR = Path.cwd()
DATA_DIR = ROOT_DIR / "data"
REPORTS_DIR = ROOT_DIR / "reports"
DB_PATH = DATA_DIR / "patent_pipeline.db"

def create_visualizations():
    print(f"[{datetime.now()}] Connecting to database...")
    conn = sqlite3.connect(DB_PATH)

    print(f"[{datetime.now()}] Creating visualizations...")

    # 1. Patent trends over time
    print(f"[{datetime.now()}] Creating patent trends chart...")
    trends_df = pd.read_sql_query("""
        SELECT year, COUNT(*) as patents
        FROM patents
        WHERE year IS NOT NULL AND year > 1900
        GROUP BY year
        ORDER BY year
    """, conn)

    plt.figure(figsize=(12, 6))
    plt.plot(trends_df['year'], trends_df['patents'], linewidth=2, marker='o', markersize=3)
    plt.title('Patent Filings by Year (1976-2023)', fontsize=16, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Number of Patents', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'patent_trends.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Top inventors bar chart
    print(f"[{datetime.now()}] Creating top inventors chart...")
    inventors_df = pd.read_sql_query("""
        SELECT i.name, COUNT(DISTINCT r.patent_id) as patents
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.inventor_id, i.name
        ORDER BY patents DESC
        LIMIT 20
    """, conn)

    plt.figure(figsize=(12, 8))
    bars = plt.barh(range(len(inventors_df)), inventors_df['patents'])
    plt.yticks(range(len(inventors_df)), inventors_df['name'])
    plt.title('Top 20 Inventors by Patent Count', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Patents', fontsize=12)
    plt.ylabel('Inventor Name', fontsize=12)

    # Add value labels on bars
    for i, (bar, count) in enumerate(zip(bars, inventors_df['patents'])):
        plt.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                f'{count:,}', ha='left', va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'top_inventors_chart.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Top companies analysis
    print(f"[{datetime.now()}] Creating company analysis chart...")
    companies_df = pd.read_sql_query("""
        SELECT c.name, COUNT(DISTINCT r.patent_id) as patents
        FROM companies c
        JOIN relationships r ON c.company_id = r.company_id
        GROUP BY c.company_id, c.name
        ORDER BY patents DESC
        LIMIT 15
    """, conn)

    plt.figure(figsize=(14, 8))
    bars = plt.bar(range(len(companies_df)), companies_df['patents'])
    plt.xticks(range(len(companies_df)), companies_df['name'], rotation=45, ha='right')
    plt.title('Top 15 Companies by Patent Count', fontsize=16, fontweight='bold')
    plt.xlabel('Company Name', fontsize=12)
    plt.ylabel('Number of Patents', fontsize=12)

    # Add value labels on bars
    for i, (bar, count) in enumerate(zip(bars, companies_df['patents'])):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
                f'{count:,}', ha='center', va='bottom', fontsize=9, rotation=90)

    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'company_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Country distribution (excluding unknown)
    print(f"[{datetime.now()}] Creating country distribution chart...")
    countries_df = pd.read_sql_query("""
        SELECT i.country, COUNT(DISTINCT r.patent_id) as patents
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        WHERE i.country IS NOT NULL AND i.country != '' AND i.country != 'Unknown'
        GROUP BY i.country
        ORDER BY patents DESC
        LIMIT 20
    """, conn)

    plt.figure(figsize=(12, 8))
    plt.pie(countries_df['patents'], labels=countries_df['country'],
            autopct='%1.1f%%', startangle=90)
    plt.title('Patent Distribution by Inventor Country (Top 20)', fontsize=16, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'country_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 5. Interactive plotly charts for dashboard
    print(f"[{datetime.now()}] Creating interactive charts...")

    # Interactive patent trends
    fig_trends = px.line(trends_df, x='year', y='patents',
                        title='Patent Filings Over Time',
                        labels={'year': 'Year', 'patents': 'Number of Patents'})
    fig_trends.write_html(REPORTS_DIR / 'interactive_trends.html')

    # Interactive top inventors
    fig_inventors = px.bar(inventors_df.head(10), x='patents', y='name',
                          title='Top 10 Inventors by Patent Count',
                          labels={'patents': 'Number of Patents', 'name': 'Inventor'},
                          orientation='h')
    fig_inventors.write_html(REPORTS_DIR / 'interactive_inventors.html')

    # Interactive top companies
    fig_companies = px.bar(companies_df.head(10), x='name', y='patents',
                          title='Top 10 Companies by Patent Count',
                          labels={'name': 'Company', 'patents': 'Number of Patents'})
    fig_companies.write_html(REPORTS_DIR / 'interactive_companies.html')

    conn.close()

    print(f"[{datetime.now()}] Visualizations created successfully!")
    print(f"Static charts saved to: {REPORTS_DIR}")
    print(f"Interactive charts saved as HTML files")

if __name__ == "__main__":
    try:
        create_visualizations()
    except Exception as e:
        print(f"Error creating visualizations: {e}")
        import traceback
        traceback.print_exc()