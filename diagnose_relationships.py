#!/usr/bin/env python3
"""Diagnose relationship loading issues."""

import sys
import os
import pandas as pd
from pathlib import Path
import zipfile

# Use current directory as root since we'll run from project root
ROOT_DIR = Path.cwd()
DATA_DIR = ROOT_DIR / "data"

print(f"Working directory: {ROOT_DIR}")
print(f"Data directory: {DATA_DIR}")
print(f"Data dir exists: {DATA_DIR.exists()}")

def read_tsv_chunks(path: Path, usecols=None, chunksize=100000) -> pd.DataFrame:
    """Read TSV file with chunking support for large files."""
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            tsv_names = [name for name in archive.namelist() if name.endswith(".tsv")]
            if not tsv_names:
                raise FileNotFoundError(f"No TSV files found in {path}")
            with archive.open(tsv_names[0]) as f:
                for chunk in pd.read_csv(f, sep="\t", usecols=usecols, chunksize=chunksize, low_memory=False):
                    yield chunk
    else:
        for chunk in pd.read_csv(path, sep="\t", usecols=usecols, chunksize=chunksize, low_memory=False):
            yield chunk

def check_files():
    print("Checking available files...")
    inventor_file = DATA_DIR / "g_inventor_disambiguated.tsv.zip"
    assignee_file = DATA_DIR / "g_assignee_disambiguated.tsv.zip"
    
    if inventor_file.exists():
        print(f"✓ Found {inventor_file.name}")
    else:
        print(f"✗ Missing {inventor_file.name}")
        return False
        
    if assignee_file.exists():
        print(f"✓ Found {assignee_file.name}")
    else:
        print(f"✗ Missing {assignee_file.name}")
        return False
    
    return True

def sample_inventor_data():
    print("\n=== Sampling Inventor Data ===")
    inventor_file = DATA_DIR / "g_inventor_disambiguated.tsv.zip"
    
    # Check available columns
    with zipfile.ZipFile(inventor_file) as archive:
        tsv_names = [name for name in archive.namelist() if name.endswith(".tsv")]
        if tsv_names:
            with archive.open(tsv_names[0]) as f:
                df = pd.read_csv(f, sep="\t", nrows=5, low_memory=False)
                print(f"Columns: {list(df.columns)}")
                print(f"\nFirst 5 rows:")
                print(df[["patent_id", "inventor_id"] if all(c in df.columns for c in ["patent_id", "inventor_id"]) else list(df.columns)[:5]])
                
                # Count unique patents and inventors
                with archive.open(tsv_names[0]) as f2:
                    df_full = pd.read_csv(f2, sep="\t", usecols=["patent_id", "inventor_id"] if all(c in df.columns for c in ["patent_id", "inventor_id"]) else None, low_memory=False, nrows=100000)
                    print(f"\nIn first 100k rows:")
                    print(f"  Unique patents: {df_full['patent_id'].nunique() if 'patent_id' in df_full.columns else 'N/A'}")
                    print(f"  Unique inventors: {df_full['inventor_id'].nunique() if 'inventor_id' in df_full.columns else 'N/A'}")
                    print(f"  Total rows: {len(df_full)}")

def sample_assignee_data():
    print("\n=== Sampling Assignee Data ===")
    assignee_file = DATA_DIR / "g_assignee_disambiguated.tsv.zip"
    
    with zipfile.ZipFile(assignee_file) as archive:
        tsv_names = [name for name in archive.namelist() if name.endswith(".tsv")]
        if tsv_names:
            with archive.open(tsv_names[0]) as f:
                df = pd.read_csv(f, sep="\t", nrows=5, low_memory=False)
                print(f"Columns: {list(df.columns)}")
                print(f"\nFirst 5 rows:")
                print(df[["patent_id", "assignee_id"] if all(c in df.columns for c in ["patent_id", "assignee_id"]) else list(df.columns)[:5]])
                
                # Count unique patents and assignees
                with archive.open(tsv_names[0]) as f2:
                    df_full = pd.read_csv(f2, sep="\t", usecols=["patent_id", "assignee_id"] if all(c in df.columns for c in ["patent_id", "assignee_id"]) else None, low_memory=False, nrows=100000)
                    print(f"\nIn first 100k rows:")
                    print(f"  Unique patents: {df_full['patent_id'].nunique() if 'patent_id' in df_full.columns else 'N/A'}")
                    print(f"  Unique assignees: {df_full['assignee_id'].nunique() if 'assignee_id' in df_full.columns else 'N/A'}")
                    print(f"  Total rows: {len(df_full)}")

def test_merge():
    print("\n=== Testing Merge ===")
    inventor_file = DATA_DIR / "g_inventor_disambiguated.tsv.zip"
    assignee_file = DATA_DIR / "g_assignee_disambiguated.tsv.zip"
    
    # Load small samples
    print("Loading sample inventor data...")
    inventor_patents = []
    chunk_count = 0
    for chunk in read_tsv_chunks(inventor_file, usecols=["patent_id", "inventor_id"], chunksize=50000):
        inventor_patents.append(chunk[["patent_id", "inventor_id"]].drop_duplicates())
        chunk_count += 1
        if chunk_count >= 2:  # Just 2 chunks = 100k rows
            break
    inventor_df = pd.concat(inventor_patents, ignore_index=True).drop_duplicates()
    print(f"Loaded {len(inventor_df)} inventor-patent links")
    
    print("Loading sample assignee data...")
    assignee_patents = []
    chunk_count = 0
    for chunk in read_tsv_chunks(assignee_file, usecols=["patent_id", "assignee_id"], chunksize=50000):
        assignee_patents.append(chunk[["patent_id", "assignee_id"]].drop_duplicates())
        chunk_count += 1
        if chunk_count >= 2:
            break
    assignee_df = pd.concat(assignee_patents, ignore_index=True).drop_duplicates()
    assignee_df = assignee_df.rename(columns={"assignee_id": "company_id"})
    print(f"Loaded {len(assignee_df)} assignee-patent links")
    
    print(f"\nMerging on patent_id (INNER join)...")
    merged = inventor_df.merge(assignee_df, on="patent_id", how="inner")
    print(f"Merged result: {len(merged)} rows")
    if len(merged) > 0:
        print(f"✓ Merge successful!")
        print(merged.head())
    else:
        print(f"✗ Merge produced empty result - checking overlapping patents...")
        common_patents = set(inventor_df["patent_id"]) & set(assignee_df["patent_id"])
        print(f"  Overlapping patents: {len(common_patents)}/{max(len(inventor_df), len(assignee_df))}")
        if common_patents:
            sample_patent = list(common_patents)[0]
            print(f"\n  Sample patent {sample_patent}:")
            print(f"    Inventors: {inventor_df[inventor_df['patent_id'] == sample_patent].shape[0]}")
            print(f"    Assignees: {assignee_df[assignee_df['patent_id'] == sample_patent].shape[0]}")

if __name__ == "__main__":
    try:
        if check_files():
            sample_inventor_data()
            sample_assignee_data()
            test_merge()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
