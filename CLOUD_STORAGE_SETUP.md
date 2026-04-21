# ☁️ Cloud Storage Setup for Database

Since the database is too large (120MB) to commit to GitHub, use cloud storage and have Streamlit Cloud download it on startup.

## 🎯 Choose Your Storage Option

### Option 1: Google Drive (Easiest) ⭐

**Steps:**

1. **Upload Database**
   - Go to [drive.google.com](https://drive.google.com)
   - Upload `data/patent_pipeline.db`
   - Right-click → Share → "Anyone with the link"
   - Copy the share link

2. **Get Direct Download URL**
   - Share link looks like: `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`
   - Convert to download URL:
     ```
     https://drive.google.com/uc?id=FILE_ID&export=download
     ```

3. **Add to Streamlit Cloud**
   - Go to your app in Streamlit Cloud
   - Click ⋮ → Settings → Secrets
   - Add:
     ```toml
     DATABASE_URL = "https://drive.google.com/uc?id=YOUR_FILE_ID&export=download"
     ```

---

### Option 2: AWS S3

**Steps:**

1. **Create AWS Account** (free tier available)
   - Go to [aws.amazon.com](https://aws.amazon.com)

2. **Create S3 Bucket**
   - Services → S3 → Create Bucket
   - Name: `patent-intelligence`
   - Unblock public access (only for downloads)

3. **Upload Database**
   - Upload `data/patent_pipeline.db`
   - Right-click → Properties → copy Object URL

4. **Make File Public** (Optional - for direct access)
   - Select file → Object ACL → Make public

5. **Add to Streamlit Cloud**
   - Secrets → Add:
     ```toml
     DATABASE_URL = "https://your-bucket.s3.amazonaws.com/patent_pipeline.db"
     ```

---

### Option 3: OneDrive

**Steps:**

1. **Upload to OneDrive**
   - Go to [onedrive.com](https://onedrive.com)
   - Upload `data/patent_pipeline.db`

2. **Get Share Link**
   - Right-click → Share
   - Get the link

3. **Convert to Download URL**
   - Share link: `https://onedrive.live.com/...`
   - Modify last parameter from `e=sharing` to `download=1`

4. **Add to Streamlit Cloud Secrets**

---

### Option 4: GitHub Releases

**Steps:**

1. **Create GitHub Release**
   - Go to your GitHub repo
   - Releases → Create Release
   - Upload `patent_pipeline.db` as asset
   - Click "Create Release"

2. **Get Download URL**
   - Right-click asset → Copy link
   - URL looks like: `https://github.com/username/repo/releases/download/v1.0/patent_pipeline.db`

3. **Add to Streamlit Cloud Secrets**

---

## 🔐 Setting Up Streamlit Cloud Secrets

1. **Go to Streamlit Cloud**
   - Visit [streamlit.io/cloud](https://streamlit.io/cloud)
   - Find your deployed app

2. **Access Settings**
   - Click ⋮ (menu) → Settings

3. **Add Secrets**
   - Click "Secrets"
   - Paste your DATABASE_URL:
     ```toml
     DATABASE_URL = "your-download-url-here"
     ```
   - Save

4. **Redeploy**
   - App will automatically restart
   - Database will download on first access

---

## 🚀 How It Works

1. **App Starts**: Streamlit Cloud runs `initialize_database()`
2. **Check Local**: Looks for `data/patent_pipeline.db` (not found)
3. **Detect Cloud**: Sees `STREAMLIT_CLOUD` environment variable
4. **Download**: Reads `DATABASE_URL` from secrets
5. **Cache**: Stores downloaded database in app's file system
6. **Run**: Dashboard queries the cached database

---

## 💾 Database Size Considerations

- **Database Size**: ~120 MB
- **Download Time**: 1-2 minutes on first load
- **After First Load**: Instant access (cached)
- **Free Tier Disk**: 1 GB available
- **Storage Path**: `/tmp/` (temporary, resets on app restart)

---

## ⚠️ Important Notes

### For Large Files (>100MB)

If using GitHub Releases:

```bash
# Install Git LFS first
git lfs install

# Track large files
git lfs track "*.db"

# Commit and push
git add .gitattributes
git commit -m "Track database with LFS"
git push
```

### For AWS S3

Consider using signed URLs for security:

```python
import boto3
from botocore.exceptions import ClientError

def get_s3_signed_url(bucket_name, object_name, expiration=3600):
    """Generate a signed URL for S3 object"""
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_name},
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        return None
```

---

## 🔄 Keeping Database Updated

### Local Development

```bash
# Generate fresh database
python patent_pipeline.py

# Upload to cloud storage
# (Manually or via script)
```

### Streamlit Cloud

1. Update local database
2. Upload to cloud storage
3. App automatically downloads on next visit

---

## 🆘 Troubleshooting

### Database Not Downloading

**Check:**

- Is `DATABASE_URL` set in Streamlit Cloud Secrets?
- Is the URL still valid and accessible?
- Is the file the correct format?

**Fix:**

```bash
# Test URL locally
python -c "import requests; requests.get('YOUR_URL', timeout=10)"
```

### Download Too Slow

**Solutions:**

- Use regional storage closer to Streamlit servers (US-East recommended)
- Compress database before upload
- Consider upgrade to paid Streamlit tier

### Out of Storage

Streamlit Cloud temporary storage is ~1GB. Solutions:

- Delete old databases
- Use streaming to load only needed data
- Split database into smaller parts

---

## 📊 Testing Your Setup

Add this to your app to test database setup:

```python
if st.checkbox("Show Database Info"):
    db_info = {
        "Path": str(DB_PATH),
        "Exists": DB_PATH.exists(),
        "Size MB": DB_PATH.stat().st_size / (1024*1024) if DB_PATH.exists() else 0,
        "Cloud URL": os.getenv("DATABASE_URL", "Not set"),
    }
    st.json(db_info)
```

---

**Choose Google Drive for easiest setup, AWS S3 for production reliability!** ☁️
