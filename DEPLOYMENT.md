# Streamlit Cloud Deployment Guide

## Quick Deploy Steps

### 1. Go to Streamlit Cloud
Visit: https://share.streamlit.io/

### 2. Sign in with GitHub
- Click "Sign in with GitHub"
- Authorize Streamlit to access your repositories

### 3. Deploy New App
- Click "New app" button
- Select your repository: `unknowncoder84/BSEwork`
- Branch: `main`
- Main file path: `app.py`
- Click "Deploy!"

### 4. Wait for Deployment
- Streamlit will install dependencies from `requirements.txt`
- System packages from `packages.txt` will be installed
- First deployment takes 2-3 minutes

### 5. Your App is Live!
- You'll get a URL like: `https://your-app-name.streamlit.app`
- Share this URL with anyone!

## Configuration Files

✅ `requirements.txt` - Python dependencies
✅ `packages.txt` - System dependencies (chromium for web scraping)
✅ `.streamlit/config.toml` - Streamlit configuration
✅ `app.py` - Main application file

## Features Included

- 📊 Professional Dashboard UI
- 📈 Multi-stock selection with dropdown
- ➕ Add custom stocks feature
- 📥 Excel export functionality
- 📜 Download history tracking
- 🎨 Dark theme with orange accents

## Troubleshooting

### If deployment fails:
1. Check the logs in Streamlit Cloud dashboard
2. Ensure all files are pushed to GitHub
3. Verify `requirements.txt` has all dependencies
4. Check that `app.py` is in the root directory

### Common Issues:
- **Module not found**: Add missing package to `requirements.txt`
- **Port already in use**: Streamlit Cloud handles this automatically
- **Memory issues**: Optimize data processing or upgrade plan

## Local Testing Before Deploy

```bash
# Test locally first
streamlit run app.py

# If it works locally, it will work on Streamlit Cloud!
```

## Repository Structure

```
BSEwork/
├── app.py                    # Main application
├── requirements.txt          # Python dependencies
├── packages.txt             # System dependencies
├── .streamlit/
│   └── config.toml          # Streamlit config
├── components/              # Application components
├── utils/                   # Utility functions
├── tests/                   # Test files
└── README.md               # Documentation
```

## Support

For issues or questions:
- Streamlit Docs: https://docs.streamlit.io/
- Community Forum: https://discuss.streamlit.io/
- GitHub Issues: https://github.com/unknowncoder84/BSEwork/issues

---

**Note**: The app uses demo data by default. For production use with real BSE data, ensure proper API credentials and rate limiting.
