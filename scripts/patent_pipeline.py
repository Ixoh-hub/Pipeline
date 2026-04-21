import csv
import json
import os
import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
REPORTS_DIR = ROOT_DIR / "reports"
DB_PATH = DATA_DIR / "patent_pipeline.db"
CLEAN_PATENTS_PATH = DATA_DIR / "clean_patents.csv"
CLEAN_INVENTORS_PATH = DATA_DIR / "clean_inventors.csv"
CLEAN_COMPANIES_PATH = DATA_DIR / "clean_companies.csv"
TOP_INVENTORS_PATH = REPORTS_DIR / "top_inventors.csv"
TOP_COMPANIES_PATH = REPORTS_DIR / "top_companies.csv"
COUNTRY_TRENDS_PATH = REPORTS_DIR / "country_trends.csv"
JSON_REPORT_PATH = REPORTS_DIR / "patent_report.json"
SCHEMA_SQL_PATH = ROOT_DIR / "sql" / "schema.sql"


def normalize_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def get_tsv_source(name: str) -> Path | None:
    directory = DATA_DIR / name
    if directory.is_dir():
        candidate = directory / f"{name}.tsv"
        if candidate.exists():
            return candidate
        for child in directory.iterdir():
            if child.suffix == ".tsv":
                return child
    zip_path = DATA_DIR / f"{name}.tsv.zip"
    if zip_path.exists():
        return zip_path
    return None


def read_tsv(path: Path, usecols=None) -> pd.DataFrame:
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            tsv_names = [name for name in archive.namelist() if name.endswith(".tsv")]
            if not tsv_names:
                raise FileNotFoundError(f"No TSV file inside {path}")
            with archive.open(tsv_names[0]) as stream:
                return pd.read_csv(stream, sep="\t", dtype=str, usecols=usecols, low_memory=False)
    return pd.read_csv(path, sep="\t", dtype=str, usecols=usecols, low_memory=False)


def read_tsv_chunks(path: Path, usecols=None, chunksize: int = 100_000):
    if path.suffix == ".zip":
        archive = zipfile.ZipFile(path)
        tsv_names = [name for name in archive.namelist() if name.endswith(".tsv")]
        if not tsv_names:
            raise FileNotFoundError(f"No TSV file inside {path}")
        stream = archive.open(tsv_names[0])
        return pd.read_csv(stream, sep="\t", dtype=str, usecols=usecols, chunksize=chunksize, low_memory=False)
    return pd.read_csv(path, sep="\t", dtype=str, usecols=usecols, chunksize=chunksize, low_memory=False)


def read_columns(path: Path) -> list[str]:
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            tsv_names = [name for name in archive.namelist() if name.endswith(".tsv")]
            if not tsv_names:
                return []
            with archive.open(tsv_names[0]) as stream:
                return pd.read_csv(stream, sep="\t", nrows=0).columns.tolist()
    return pd.read_csv(path, sep="\t", nrows=0).columns.tolist()


def parse_year(date_text: str) -> int | None:
    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y"]:
        try:
            return datetime.strptime(date_text, fmt).year
        except (ValueError, TypeError):
            continue
    return None


def load_patents() -> pd.DataFrame:
    source = get_tsv_source("g_patent")
    if source is None:
        raise FileNotFoundError("Missing g_patent.tsv or g_patent.tsv.zip in data/")

    columns = read_columns(source)
    selected = ["patent_id", "patent_date", "patent_title"]
    if "patent_abstract" in columns:
        selected.append("patent_abstract")

    frames = []
    for chunk in read_tsv_chunks(source, usecols=[c for c in selected if c in columns]):
        chunk = chunk.fillna("")
        chunk = chunk.rename(columns={"patent_title": "title", "patent_date": "filing_date"})
        if "patent_abstract" in chunk.columns:
            chunk = chunk.rename(columns={"patent_abstract": "abstract"})
        else:
            chunk["abstract"] = ""
        frames.append(chunk[["patent_id", "title", "abstract", "filing_date"]])

    patent_df = pd.concat(frames, ignore_index=True)
    patent_df = patent_df.drop_duplicates(subset=["patent_id"]).reset_index(drop=True)
    patent_df["year"] = patent_df["filing_date"].apply(lambda x: parse_year(normalize_text(x)) or "")
    return patent_df[["patent_id", "title", "abstract", "filing_date", "year"]]


def load_location_data() -> pd.DataFrame | None:
    source = get_tsv_source("g_location")
    if source is None:
        return None
    columns = read_columns(source)
    usecols = [col for col in ["location_id", "country", "country_name"] if col in columns]
    if not usecols:
        return None

    frames = []
    for chunk in read_tsv_chunks(source, usecols=usecols):
        frames.append(chunk.fillna(""))
    df = pd.concat(frames, ignore_index=True)
    if "country" not in df.columns and "country_name" in df.columns:
        df = df.rename(columns={"country_name": "country"})
    return df.drop_duplicates(subset=["location_id"]).reset_index(drop=True)


def load_inventors(location_map: pd.DataFrame | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    source = get_tsv_source("g_inventor_disambiguated") or get_tsv_source("g_inventor_not_disambiguated")
    if source is None:
        raise FileNotFoundError("Missing g_inventor_disambiguated.tsv or g_inventor_not_disambiguated.tsv in data/")

    columns = read_columns(source)
    usecols = [col for col in ["patent_id", "inventor_id", "disambig_inventor_name_first", "disambig_inventor_name_last", "inventor_name", "location_id"] if col in columns]

    inventor_frames = []
    patent_frames = []
    for chunk in read_tsv_chunks(source, usecols=usecols):
        chunk = chunk.fillna("")
        chunk["name"] = chunk.apply(
            lambda row: normalize_text(f"{row.get('disambig_inventor_name_first', '')} {row.get('disambig_inventor_name_last', '')}")
            or normalize_text(row.get("inventor_name", "")),
            axis=1,
        )
        inventor_frames.append(chunk[["inventor_id", "name", "location_id"]].drop_duplicates(subset=["inventor_id"]))
        patent_frames.append(chunk[["patent_id", "inventor_id"]].drop_duplicates())

    inventors_df = pd.concat(inventor_frames, ignore_index=True).drop_duplicates(subset=["inventor_id"]).reset_index(drop=True)
    inventors_df["inventor_id"] = inventors_df["inventor_id"].apply(normalize_text)
    inventors_df["name"] = inventors_df["name"].apply(lambda x: normalize_text(x) or "Unknown")
    inventors_df["location_id"] = inventors_df["location_id"].apply(normalize_text)

    if location_map is not None and "location_id" in inventors_df.columns:
        inventors_df = inventors_df.merge(location_map, on="location_id", how="left")
        inventors_df["country"] = inventors_df["country"].replace("", "Unknown")
    else:
        inventors_df["country"] = "Unknown"
    inventors_df = inventors_df[["inventor_id", "name", "country"]]

    inventor_patents = pd.concat(patent_frames, ignore_index=True).drop_duplicates().reset_index(drop=True)
    inventor_patents["patent_id"] = inventor_patents["patent_id"].apply(normalize_text)
    inventor_patents["inventor_id"] = inventor_patents["inventor_id"].apply(normalize_text)
    inventor_patents = inventor_patents[(inventor_patents["patent_id"] != "") & (inventor_patents["inventor_id"] != "")]
    return inventors_df, inventor_patents


def load_assignees(location_map: pd.DataFrame | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    source = get_tsv_source("g_assignee_disambiguated") or get_tsv_source("g_assignee_not_disambiguated")
    if source is None:
        raise FileNotFoundError("Missing g_assignee_disambiguated.tsv or g_assignee_not_disambiguated.tsv in data/")

    columns = read_columns(source)
    usecols = [col for col in ["patent_id", "assignee_id", "disambig_assignee_organization", "disambig_assignee_individual_name_first", "disambig_assignee_individual_name_last", "assignee_name", "location_id"] if col in columns]

    company_frames = []
    patent_frames = []
    for chunk in read_tsv_chunks(source, usecols=usecols):
        chunk = chunk.fillna("")
        chunk["name"] = chunk.apply(
            lambda row: normalize_text(row.get("disambig_assignee_organization", ""))
            or normalize_text(f"{row.get('disambig_assignee_individual_name_first', '')} {row.get('disambig_assignee_individual_name_last', '')}")
            or normalize_text(row.get("assignee_name", "")),
            axis=1,
        )
        company_frames.append(chunk[["assignee_id", "name", "location_id"]].drop_duplicates(subset=["assignee_id"]))
        patent_frames.append(chunk[["patent_id", "assignee_id"]].drop_duplicates())

    companies_df = pd.concat(company_frames, ignore_index=True).drop_duplicates(subset=["assignee_id"]).reset_index(drop=True)
    companies_df["company_id"] = companies_df["assignee_id"].apply(normalize_text)
    companies_df["name"] = companies_df["name"].apply(lambda x: normalize_text(x) or "Unknown")
    companies_df = companies_df[["company_id", "name"]]

    assignee_patents = pd.concat(patent_frames, ignore_index=True).drop_duplicates().reset_index(drop=True)
    assignee_patents["patent_id"] = assignee_patents["patent_id"].apply(normalize_text)
    assignee_patents["company_id"] = assignee_patents["assignee_id"].apply(normalize_text)
    assignee_patents = assignee_patents[(assignee_patents["patent_id"] != "") & (assignee_patents["company_id"] != "")]
    assignee_patents = assignee_patents[["patent_id", "company_id"]]
    return companies_df, assignee_patents


def load_relationships(inventor_patents: pd.DataFrame, assignee_patents: pd.DataFrame) -> pd.DataFrame:
    """Create a three-way relationship table linking patents to inventors and companies.
    
    For each patent that has both inventor(s) and assignee(s), create rows combining them.
    This allows analysis of which companies employ which inventors for which patents.
    """
    # Rename assignee column in assignee_patents to company_id for merging
    assignee_copy = assignee_patents.copy()
    assignee_copy = assignee_copy.rename(columns={"company_id": "assignee_id"}) if "company_id" in assignee_copy.columns else assignee_copy
    if "company_id" not in assignee_copy.columns and "assignee_id" in assignee_copy.columns:
        pass  # Already has assignee_id
    
    # For each patent, merge all its inventors with all its assignees
    # This creates a cartesian product for each patent: all inventors × all assignees
    merged = inventor_patents.merge(assignee_patents, on="patent_id", how="inner")
    relationships = merged.drop_duplicates().reset_index(drop=True)
    
    # Ensure columns are in the right order
    if "inventor_id" in relationships.columns and "company_id" in relationships.columns:
        relationships = relationships[["patent_id", "inventor_id", "company_id"]]
    
    return relationships


def write_clean_files(patents_df: pd.DataFrame, inventors_df: pd.DataFrame, companies_df: pd.DataFrame):
    patents_df.to_csv(CLEAN_PATENTS_PATH, index=False)
    inventors_df.to_csv(CLEAN_INVENTORS_PATH, index=False)
    companies_df.to_csv(CLEAN_COMPANIES_PATH, index=False)
    print(f"Saved clean files to {DATA_DIR}")


def create_database(path: Path, patents_df: pd.DataFrame, inventors_df: pd.DataFrame, companies_df: pd.DataFrame, relationships_df: pd.DataFrame):
    conn = sqlite3.connect(path)
    with conn:
        with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        patents_df.to_sql("patents", conn, if_exists="replace", index=False)
        inventors_df.to_sql("inventors", conn, if_exists="replace", index=False)
        companies_df.to_sql("companies", conn, if_exists="replace", index=False)
        relationships_df.to_sql("relationships", conn, if_exists="replace", index=False)
    print(f"Created SQLite database at {path}")
    return conn


def run_analysis(conn: sqlite3.Connection) -> dict:
    queries = {
        "top_inventors": (
            "SELECT i.name, COUNT(DISTINCT r.patent_id) AS patents "
            "FROM inventors i "
            "JOIN relationships r ON i.inventor_id = r.inventor_id "
            "GROUP BY i.name ORDER BY patents DESC, i.name LIMIT 10"
        ),
        "top_companies": (
            "SELECT c.name, COUNT(DISTINCT r.patent_id) AS patents "
            "FROM companies c "
            "JOIN relationships r ON c.company_id = r.company_id "
            "GROUP BY c.name ORDER BY patents DESC, c.name LIMIT 10"
        ),
        "top_countries": (
            "SELECT i.country AS country, COUNT(DISTINCT r.patent_id) AS patents "
            "FROM inventors i "
            "JOIN relationships r ON i.inventor_id = r.inventor_id "
            "GROUP BY i.country ORDER BY patents DESC, i.country LIMIT 10"
        ),
        "country_trends": (
            "SELECT p.year, COUNT(*) AS patents "
            "FROM patents p GROUP BY p.year ORDER BY p.year"
        ),
    }
    results = {}
    for name, sql in queries.items():
        results[name] = pd.read_sql_query(sql, conn)
    results["top_inventors"].to_csv(TOP_INVENTORS_PATH, index=False)
    results["top_companies"].to_csv(TOP_COMPANIES_PATH, index=False)
    results["country_trends"].to_csv(COUNTRY_TRENDS_PATH, index=False)
    print(f"Saved report CSVs to {REPORTS_DIR}")
    return results


def write_json_report(results: dict, total_patents: int):
    report = {
        "total_patents": total_patents,
        "top_inventors": results["top_inventors"].to_dict(orient="records"),
        "top_companies": results["top_companies"].to_dict(orient="records"),
        "top_countries": results["top_countries"].to_dict(orient="records"),
    }
    with open(JSON_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Saved JSON report to {JSON_REPORT_PATH}")
    return report


def print_console_report(report: dict, total_patents: int):
    top_inventors = report["top_inventors"][:3]
    top_companies = report["top_companies"][:3]
    top_countries = report["top_countries"][:3]
    print("\n================== PATENT REPORT ===================")
    print(f"Total Patents: {total_patents}")
    print(
        "Top Inventors: "
        + ", ".join([f"{i+1}. {row['name']} - {row['patents']}" for i, row in enumerate(top_inventors)])
    )
    print(
        "Top Companies: "
        + ", ".join([f"{i+1}. {row['name']} - {row['patents']}" for i, row in enumerate(top_companies)])
    )
    print(
        "Top Countries: "
        + ", ".join([f"{i+1}. {row['country']} - {row['patents']}" for i, row in enumerate(top_countries)])
    )
    print("====================================================\n")


def ensure_directories():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    ensure_directories()
    
    print(f"[{datetime.now()}] Starting patent pipeline...")
    
    print(f"[{datetime.now()}] Loading location data...")
    location_map = load_location_data()
    print(f"[{datetime.now()}] Location data: {len(location_map) if location_map is not None else 0} records")
    
    print(f"[{datetime.now()}] Loading patents...")
    patents_df = load_patents()
    print(f"[{datetime.now()}] Patents loaded: {len(patents_df)} records")
    
    print(f"[{datetime.now()}] Loading inventors...")
    inventors_df, inventor_patents = load_inventors(location_map)
    print(f"[{datetime.now()}] Inventors loaded: {len(inventors_df)} records, {len(inventor_patents)} patent links")
    
    print(f"[{datetime.now()}] Loading assignees...")
    companies_df, assignee_patents = load_assignees(location_map)
    print(f"[{datetime.now()}] Companies loaded: {len(companies_df)} records, {len(assignee_patents)} patent links")
    
    print(f"[{datetime.now()}] Loading relationships...")
    relationships_df = load_relationships(inventor_patents, assignee_patents)
    print(f"[{datetime.now()}] Relationships loaded: {len(relationships_df)} records")
    
    print(f"[{datetime.now()}] Writing clean files...")
    write_clean_files(patents_df, inventors_df, companies_df)
    print(f"[{datetime.now()}] Clean files saved")
    
    print(f"[{datetime.now()}] Creating database...")
    conn = create_database(DB_PATH, patents_df, inventors_df, companies_df, relationships_df)
    print(f"[{datetime.now()}] Database created")
    
    print(f"[{datetime.now()}] Running analysis queries...")
    results = run_analysis(conn)
    print(f"[{datetime.now()}] Analysis complete")
    
    print(f"[{datetime.now()}] Writing JSON report...")
    report = write_json_report(results, total_patents=len(patents_df))
    print(f"[{datetime.now()}] JSON report written")
    
    print(f"[{datetime.now()}] Printing console report...")
    print_console_report(report, total_patents=len(patents_df))
    print(f"[{datetime.now()}] Pipeline complete!")
    
    conn.close()


if __name__ == "__main__":
    main()
