#!/usr/bin/env python3
"""Advanced patent category analysis using CPC classifications."""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import zipfile
import gzip

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

ROOT_DIR = Path.cwd()
DATA_DIR = ROOT_DIR / "data"
REPORTS_DIR = ROOT_DIR / "reports"
DB_PATH = DATA_DIR / "patent_pipeline.db"

def load_cpc_data():
    """Load CPC classification data if available."""
    cpc_file = DATA_DIR / "g_cpc_current.tsv"
    cpc_zip = DATA_DIR / "g_cpc_current.tsv.zip"

    if cpc_file.exists():
        print(f"[{datetime.now()}] Loading CPC data from {cpc_file}")
        return pd.read_csv(cpc_file, sep='\t', dtype=str, chunksize=100000)
    elif cpc_zip.exists():
        print(f"[{datetime.now()}] Loading CPC data from {cpc_zip}")
        with zipfile.ZipFile(cpc_zip, 'r') as zf:
            # Get the first file in the zip
            filename = zf.namelist()[0]
            with zf.open(filename) as f:
                return pd.read_csv(f, sep='\t', dtype=str, chunksize=100000)
    else:
        print(f"[{datetime.now()}] CPC data not found. Skipping category analysis.")
        return None

def analyze_categories():
    print(f"[{datetime.now()}] Starting advanced patent category analysis...")

    conn = sqlite3.connect(DB_PATH)

    # Check if CPC data is available
    cpc_chunks = load_cpc_data()
    if cpc_chunks is None:
        print(f"[{datetime.now()}] No CPC data available. Performing basic category analysis...")

        # Basic analysis without CPC data
        basic_category_analysis(conn)
        conn.close()
        return

    # Create CPC table
    print(f"[{datetime.now()}] Creating CPC classifications table...")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cpc_classifications (
            patent_id TEXT,
            cpc_section TEXT,
            cpc_class TEXT,
            cpc_subclass TEXT,
            cpc_group TEXT,
            cpc_subgroup TEXT,
            category TEXT
        )
    """)

    # Process CPC data in chunks
    total_processed = 0
    for chunk in cpc_chunks:
        # Clean and process chunk
        chunk = chunk[['patent_id', 'cpc_section', 'cpc_class', 'cpc_subclass', 'cpc_group', 'cpc_subgroup']]
        chunk['category'] = chunk['cpc_section'] + chunk['cpc_class']

        # Insert chunk
        chunk.to_sql('cpc_classifications', conn, if_exists='append', index=False)
        total_processed += len(chunk)
        print(f"[{datetime.now()}] Processed {total_processed:,} CPC records...")

    # Create indexes
    print(f"[{datetime.now()}] Creating indexes on CPC data...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cpc_patent ON cpc_classifications(patent_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cpc_category ON cpc_classifications(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cpc_section ON cpc_classifications(cpc_section)")

    conn.commit()

    # Perform advanced analysis
    advanced_category_analysis(conn)

    conn.close()
    print(f"[{datetime.now()}] Category analysis complete!")

def basic_category_analysis(conn):
    """Basic analysis when CPC data is not available."""
    print(f"[{datetime.now()}] Performing basic patent analysis...")

    # Analyze patents by year and basic metrics
    year_stats = pd.read_sql_query("""
        SELECT
            year,
            COUNT(*) as total_patents,
            COUNT(DISTINCT title) as unique_titles,
            AVG(LENGTH(title)) as avg_title_length,
            AVG(LENGTH(abstract)) as avg_abstract_length
        FROM patents
        WHERE year IS NOT NULL AND year > 1900
        GROUP BY year
        ORDER BY year
    """, conn)

    # Plot patent complexity over time
    plt.figure(figsize=(12, 6))
    plt.plot(year_stats['year'], year_stats['avg_title_length'], label='Avg Title Length', marker='o')
    plt.plot(year_stats['year'], year_stats['avg_abstract_length'], label='Avg Abstract Length', marker='s')
    plt.title('Patent Complexity Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Year')
    plt.ylabel('Average Length (characters)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'patent_complexity_trends.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Inventor collaboration analysis
    collaboration_stats = pd.read_sql_query("""
        SELECT
            patent_count,
            COUNT(*) as frequency
        FROM (
            SELECT patent_id, COUNT(*) as patent_count
            FROM relationships
            GROUP BY patent_id
        )
        GROUP BY patent_count
        ORDER BY patent_count
        LIMIT 10
    """, conn)

    plt.figure(figsize=(10, 6))
    plt.bar(collaboration_stats['patent_count'], collaboration_stats['frequency'])
    plt.title('Patent Collaboration Patterns', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Inventors per Patent')
    plt.ylabel('Number of Patents')
    plt.xticks(collaboration_stats['patent_count'])
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'collaboration_patterns.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"[{datetime.now()}] Basic analysis visualizations saved.")

def advanced_category_analysis(conn):
    """Advanced analysis with CPC classification data."""
    print(f"[{datetime.now()}] Performing advanced category analysis...")

    # Top CPC categories
    category_stats = pd.read_sql_query("""
        SELECT
            category,
            COUNT(DISTINCT patent_id) as patents,
            COUNT(*) as classifications
        FROM cpc_classifications
        GROUP BY category
        ORDER BY patents DESC
        LIMIT 20
    """, conn)

    plt.figure(figsize=(12, 8))
    bars = plt.barh(range(len(category_stats)), category_stats['patents'])
    plt.yticks(range(len(category_stats)), category_stats['category'])
    plt.title('Top 20 CPC Categories by Patent Count', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Patents')

    for i, (bar, count) in enumerate(zip(bars, category_stats['patents'])):
        plt.text(bar.get_width() + 1000, bar.get_y() + bar.get_height()/2,
                f'{count:,}', ha='left', va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'top_cpc_categories.png', dpi=300, bbox_inches='tight')
    plt.close()

    # CPC sections analysis
    section_stats = pd.read_sql_query("""
        SELECT
            cpc_section,
            COUNT(DISTINCT patent_id) as patents
        FROM cpc_classifications
        GROUP BY cpc_section
        ORDER BY patents DESC
    """, conn)

    plt.figure(figsize=(10, 8))
    plt.pie(section_stats['patents'], labels=section_stats['cpc_section'],
            autopct='%1.1f%%', startangle=90)
    plt.title('Patent Distribution by CPC Section', fontsize=16, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'cpc_sections_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Category trends over time
    category_trends = pd.read_sql_query("""
        SELECT
            p.year,
            c.category,
            COUNT(DISTINCT c.patent_id) as patents
        FROM cpc_classifications c
        JOIN patents p ON c.patent_id = p.patent_id
        WHERE p.year IS NOT NULL AND p.year > 2000
        GROUP BY p.year, c.category
        ORDER BY p.year, patents DESC
    """, conn)

    # Get top 5 categories for trend analysis
    top_categories = category_stats['category'].head(5).tolist()

    plt.figure(figsize=(14, 8))
    for category in top_categories:
        cat_data = category_trends[category_trends['category'] == category]
        if not cat_data.empty:
            plt.plot(cat_data['year'], cat_data['patents'], label=category, marker='o', linewidth=2)

    plt.title('Top 5 CPC Categories Trends (2000-2023)', fontsize=16, fontweight='bold')
    plt.xlabel('Year')
    plt.ylabel('Number of Patents')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'category_trends.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Company focus areas
    company_categories = pd.read_sql_query("""
        SELECT
            c.name as company,
            cpc.category,
            COUNT(DISTINCT r.patent_id) as patents
        FROM companies c
        JOIN relationships r ON c.company_id = r.company_id
        JOIN cpc_classifications cpc ON r.patent_id = cpc.patent_id
        GROUP BY c.company_id, c.name, cpc.category
        ORDER BY patents DESC
        LIMIT 50
    """, conn)

    # Create heatmap of company vs category
    pivot_table = company_categories.pivot_table(
        index='company', columns='category', values='patents', fill_value=0
    ).head(10)

    plt.figure(figsize=(14, 10))
    sns.heatmap(pivot_table, annot=True, fmt='.0f', cmap='YlOrRd')
    plt.title('Company Focus Areas by CPC Category', fontsize=16, fontweight='bold')
    plt.xlabel('CPC Category')
    plt.ylabel('Company')
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'company_focus_areas.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"[{datetime.now()}] Advanced category analysis visualizations saved.")

if __name__ == "__main__":
    try:
        analyze_categories()
    except Exception as e:
        print(f"Error in category analysis: {e}")
        import traceback
        traceback.print_exc()