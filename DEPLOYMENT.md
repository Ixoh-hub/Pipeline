# Deploying Patent Intelligence Dashboard to Streamlit Cloud

## Prerequisites

1. A GitHub account (for repository hosting)
2. A Streamlit account (free at streamlit.io)
3. Your code pushed to a GitHub repository

## Step-by-Step Deployment Guide

### Step 1: Prepare Your Repository

1. Initialize Git (if not already done):

   ```bash
   git init
   git add .
   git commit -m "Initial commit - Patent Intelligence Dashboard"
   ```

2. Create a GitHub repository:
   - Go to https://github.com/new
   - Name it "patent-pipeline" or similar
   - Create the repository (don't initialize with README)

3. Push to GitHub:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/patent-pipeline.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Prepare Database for Deployment

Since the database file is large (100MB+), we have two options:

**Option A: Download database on first run (Recommended)**

- The app will check if the database exists
- If not, it will display a message with download instructions
- Users can download from your chosen host

**Option B: Store in Cloud Storage**

- Upload database to cloud storage (Google Drive, AWS S3, etc.)
- Modify app.py to download it on startup

### Step 3: Create Streamlit Cloud Account

1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"

### Step 4: Deploy the App

1. In Streamlit Cloud dashboard, click **"New app"**
2. Select your repository: `patent-pipeline`
3. Branch: `main`
4. Main file path: `app.py`
5. Click **"Deploy"**

### Step 5: Configure Secrets (if needed)

If your app requires sensitive data:

1. Go to App Settings → Secrets
2. Add any API keys or credentials in TOML format

### Step 6: Share Your App

Once deployed, your app will have a URL like:

```
https://your-username-patent-pipeline.streamlit.app
```

Share this link with anyone to access your dashboard!

## Important Notes for Production

1. **Database Handling:**
   - The large database file (100MB+) should not be stored in the git repository
   - Store it in the GitHub LFS (Large File Storage) or use cloud storage
   - Update `.gitignore` to exclude large files

2. **Performance:**
   - Data caching is enabled for better performance
   - Queries are optimized for cloud environment
   - Consider using `@st.cache_data` decorator for expensive operations

3. **Resource Limits:**
   - Free Streamlit Cloud tier has limited resources
   - Monitor app performance and optimize queries if needed
   - Consider upgrading to paid tier for production use

4. **Updates:**
   - Simply push changes to GitHub
   - Streamlit Cloud will automatically redeploy

## Troubleshooting

### Database Not Found Error

- Ensure `data/patent_pipeline.db` is available
- Check `.gitignore` isn't preventing database from being committed

### Slow Performance

- Check database query efficiency
- Increase caching TTL in app.py
- Optimize SQL queries

### Memory Issues

- Reduce the amount of data loaded into memory
- Use pagination for large datasets
- Consider using a lighter caching strategy

## Local Testing Before Deployment

Test locally to ensure everything works:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Visit http://localhost:8501 to see your dashboard.

## Support

For Streamlit Cloud support, visit: https://docs.streamlit.io/
