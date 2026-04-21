#!/usr/bin/env python3
"""
Database download utility for Streamlit Cloud deployment.
Downloads the patent_pipeline.db from cloud storage if not available locally.
"""

import os
import sys
import requests
from pathlib import Path
import hashlib

# Configuration - UPDATE THESE WITH YOUR CLOUD STORAGE DETAILS
CLOUD_DB_URL = os.getenv("DATABASE_URL", "")  # Set as environment variable in Streamlit Cloud
DATABASE_PATH = Path("data/patent_pipeline.db")
EXPECTED_SIZE_MB = 120  # Approximate database size

def download_database(url=None):
    """Download database from cloud storage."""
    if not url:
        url = CLOUD_DB_URL
    
    if not url:
        print("⚠️  DATABASE_URL not set. Database download cannot proceed.")
        print("\nTo set up cloud storage:")
        print("1. Upload data/patent_pipeline.db to Google Drive or AWS S3")
        print("2. Get a shareable/direct download URL")
        print("3. Set it as DATABASE_URL environment variable in Streamlit Cloud secrets")
        return False
    
    try:
        print(f"📥 Downloading database from cloud storage...")
        print(f"   URL: {url[:50]}...")
        
        # Create data directory
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Download with progress
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(DATABASE_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        percent = (downloaded / total_size) * 100
                        mb = downloaded / (1024 * 1024)
                        print(f"   Progress: {percent:.1f}% ({mb:.1f}MB)", end='\r')
        
        print(f"\n✅ Database downloaded successfully!")
        print(f"   Size: {os.path.getsize(DATABASE_PATH) / (1024*1024):.1f} MB")
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()
        return False

def setup_database():
    """Ensure database is available, download if needed."""
    if DATABASE_PATH.exists():
        size_mb = os.path.getsize(DATABASE_PATH) / (1024 * 1024)
        print(f"✅ Database found ({size_mb:.1f}MB)")
        return True
    
    print("📦 Database not found locally")
    
    if os.getenv("STREAMLIT_CLOUD"):
        print("☁️  Running on Streamlit Cloud - attempting download...")
        return download_database()
    else:
        print("\n⚠️  Running locally without database")
        print("\nOptions:")
        print("1. Run 'python patent_pipeline.py' to generate database locally")
        print("2. Copy existing database to data/patent_pipeline.db")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
