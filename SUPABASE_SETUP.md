# 🚀 Supabase Setup Guide for Patent Pipeline

## Why Supabase?

Supabase provides a **free PostgreSQL database** perfect for student projects:
- ✅ **500MB free database** (our data is ~120MB)
- ✅ **No file size limits** (unlike GitHub's 100MB)
- ✅ **Direct SQL queries** (compatible with existing code)
- ✅ **Easy setup** (web interface, no servers)
- ✅ **Perfect for reproducibility** (clone repo + set env vars)

## 📋 Step-by-Step Setup

### 1. Create Supabase Account

1. Go to [supabase.com](https://supabase.com)
2. Sign up with GitHub (free)
3. Click "New Project"
4. Choose organization (your personal account)
5. Fill in project details:
   - **Name**: `patent-pipeline`
   - **Database Password**: Choose a strong password
   - **Region**: Select closest to you

### 2. Get Connection Details

After project creation (takes ~2 minutes):

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://abcdefghijklmnop.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **service_role key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

3. Go to **Settings** → **Database**
4. Copy the **Connection string** (for reference)

### 3. Upload Patent Data to Supabase

#### Option A: Use Supabase Dashboard (Easiest)

1. Go to **Table Editor** in Supabase dashboard
2. Create tables manually or use SQL editor

#### Option B: Use pgAdmin or Command Line

1. Download [pgAdmin](https://www.pgadmin.org/download/)
2. Connect using the connection string from Step 2
3. Import your SQLite data

#### Option C: Use Python Script (Recommended)

We'll create a migration script to upload your local SQLite data to Supabase.

### 4. Set Environment Variables

#### For Local Development:

Create a `.env` file in your project root:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

#### For Streamlit Cloud:

1. In Streamlit Cloud app settings
2. Go to **Secrets**
3. Add:

```toml
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "your-service-role-key"
```

### 5. Test Connection

Run locally:
```bash
python -c "from database_utils import execute_query; print(execute_query('SELECT COUNT(*) FROM patents'))"
```

Should output: Your patent count

## 🛠️ Migration Script (Optional)

If you want to automate data upload, create `migrate_to_supabase.py`:

```python
import sqlite3
import pandas as pd
from database_utils import execute_query
from pathlib import Path

def migrate_table(table_name):
    # Read from SQLite
    sqlite_conn = sqlite3.connect('data/patent_pipeline.db')
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", sqlite_conn)
    sqlite_conn.close()
    
    # Upload to Supabase (this would need custom logic for each table)
    # For large tables, use batch inserts
    print(f"Migrating {len(df)} rows to {table_name}")

# Run migration
migrate_table('patents')
migrate_table('inventors')
migrate_table('companies')
migrate_table('relationships')
```

## 📊 Database Schema

Your tables in Supabase should match:

- `patents` (id, title, abstract, year, etc.)
- `inventors` (id, name, country)
- `companies` (id, name, country)
- `relationships` (patent_id, inventor_id, company_id)

## 🔒 Security Notes

- **Never commit** `.env` files or keys to git
- Use **service_role key** only for data migration
- For production, consider **Row Level Security** (RLS) in Supabase

## 🎯 Benefits for Student Project

✅ **No storage costs** (500MB free)  
✅ **No bandwidth limits** for queries  
✅ **Professional database** (PostgreSQL)  
✅ **Easy collaboration** (share Supabase project)  
✅ **Scalable** (upgrade plan if needed)  
✅ **Reproducible** (anyone can clone + set env vars)  

## 🚀 Deploy to Streamlit Cloud

Once data is in Supabase:

1. Push clean code to GitHub (no data folder)
2. Deploy to Streamlit Cloud
3. Set secrets as above
4. App connects directly to Supabase!

---

**Questions?** Supabase has excellent documentation at [supabase.com/docs](https://supabase.com/docs)
