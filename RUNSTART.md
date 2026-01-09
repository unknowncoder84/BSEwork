# 🚀 Quantum Market Suite - Quick Start Guide

---

# 🖥️ RUN LOCALLY - Complete Step-by-Step Guide

Follow these steps carefully to run the project on your local machine.

---

## 📋 Step 1: Check Prerequisites

Before starting, make sure you have these installed:

### 1.1 Install Python 3.9+

**Check if Python is installed:**
```bash
python --version
```

**If not installed:**
- **Windows:** Download from https://www.python.org/downloads/
  - ⚠️ Check "Add Python to PATH" during installation
- **macOS:** `brew install python3`
- **Linux:** `sudo apt install python3 python3-pip`

### 1.2 Install Google Chrome

The app uses Chrome for web scraping. Download from:
https://www.google.com/chrome/

### 1.3 Install Git (Optional)

**Windows:** Download from https://git-scm.com/download/win
**macOS:** `brew install git`
**Linux:** `sudo apt install git`

---

## 📥 Step 2: Get the Project

### Option A: Clone with Git (Recommended)

```bash
git clone https://github.com/unknowncoder84/BSEwork.git
cd BSEwork
```

### Option B: Download ZIP

1. Go to https://github.com/unknowncoder84/BSEwork
2. Click green **"Code"** button
3. Click **"Download ZIP"**
4. Extract the ZIP file
5. Open terminal/command prompt in the extracted folder

---

## 🔧 Step 3: Create Virtual Environment

A virtual environment keeps dependencies isolated.

### Windows (Command Prompt):
```bash
python -m venv venv
venv\Scripts\activate
```

### Windows (PowerShell):
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

**✅ Success indicator:** You'll see `(venv)` at the start of your terminal prompt.

---

## 📦 Step 4: Install Dependencies

With your virtual environment activated, run:

```bash
pip install -r requirements.txt
```

This installs:
- `streamlit` - Web app framework
- `selenium` - Web scraping
- `pandas` - Data processing
- `openpyxl` - Excel export
- `beautifulsoup4` - HTML parsing
- And other required packages

**⏱️ This may take 2-3 minutes on first install.**

---

## ▶️ Step 5: Run the Application

```bash
streamlit run app.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

---

## 🌐 Step 6: Access the App

1. Open your web browser (Chrome recommended)
2. Go to: **http://localhost:8501**
3. The Quantum Market Suite dashboard will load

---

## 🎯 Step 7: Using the App

### Quick Workflow:

1. **Select Exchange** → Choose NSE or BSE
2. **Pick Stocks** → Select from dropdown (RELIANCE, TCS, etc.)
3. **Add Custom Stock** → Type any symbol and click "Add"
4. **Set Date Range** → Pick start and end dates
5. **Enter Strike Price** → For derivative data (e.g., 2500)
6. **Click "Process"** → Fetches and merges data
7. **Download Excel** → Click button to save results

### Features Available:
- 📊 Multi-stock selection
- 📅 Custom date ranges
- 💰 Strike price input for derivatives
- 📥 Excel export with individual tabs per stock
- 🎨 Dark/Light theme toggle
- 📝 Persistent notepad

---

## 🔄 Step 8: Stopping and Restarting

### Stop the App:
Press `Ctrl + C` in the terminal

### Restart the App:
```bash
# Make sure venv is activated
streamlit run app.py
```

### Deactivate Virtual Environment:
```bash
deactivate
```

---

## 🔁 Daily Usage (After Initial Setup)

Once set up, daily usage is simple:

```bash
# 1. Open terminal in project folder
cd BSEwork

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Run the app
streamlit run app.py

# 4. Open browser to http://localhost:8501
```

---

## ⚠️ Common Local Setup Issues

### Issue: "python not found"
**Solution:** Use `python3` instead of `python`, or add Python to PATH

### Issue: "pip not found"
**Solution:** Use `python -m pip install -r requirements.txt`

### Issue: Chrome driver errors
**Solution:** Update Chrome to latest version. The app auto-downloads the correct driver.

### Issue: Port 8501 already in use
**Solution:**
```bash
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID_NUMBER> /F

# macOS/Linux:
lsof -i :8501
kill -9 <PID>

# Or use different port:
streamlit run app.py --server.port 8502
```

### Issue: Permission denied (macOS/Linux)
**Solution:**
```bash
chmod +x venv/bin/activate
```

### Issue: SSL Certificate errors
**Solution:**
```bash
pip install --upgrade certifi
```

---

# ☁️ DEPLOY TO STREAMLIT CLOUD (Production)

---

### Step 1: Push Code to GitHub

If not already done:
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to **https://share.streamlit.io/**
2. Click **"Sign in with GitHub"**
3. Click **"New app"**
4. Configure:
   - **Repository:** `unknowncoder84/BSEwork`
   - **Branch:** `main`
   - **Main file:** `app.py`
5. Click **"Deploy!"**

### Step 3: Wait for Build

First deployment takes 2-5 minutes. You'll see:
```
Installing dependencies from requirements.txt...
Installing system packages from packages.txt...
Starting app...
```

### Step 4: Share Your App

Once deployed, you'll get a URL like:
```
https://your-app-name.streamlit.app
```

---

## Using the Application

### Main Features

| Feature | Description |
|---------|-------------|
| 📊 **Stock Selection** | Choose multiple stocks from dropdown |
| ➕ **Custom Stocks** | Add any stock symbol manually |
| 📅 **Date Range** | Select start and end dates |
| 💰 **Strike Price** | Enter strike price for derivatives |
| 📥 **Excel Export** | Download data as multi-tab Excel file |
| 🎨 **Theme Toggle** | Switch between dark/light mode |
| 📝 **Notepad** | Persistent notes saved to config |

### Workflow

1. **Select Exchange** - Choose NSE or BSE
2. **Pick Stocks** - Select from dropdown or add custom
3. **Set Date Range** - Choose your analysis period
4. **Enter Strike Price** - For derivative data
5. **Click Process** - Fetch and merge data
6. **Download Excel** - Export results

---

## Project Structure

```
BSEwork/
├── app.py                 # Main Streamlit application
├── quantum_app.py         # Alternative quantum app
├── requirements.txt       # Python dependencies
├── packages.txt           # System dependencies (Chromium)
├── config.json            # Persistent settings
├── components/            # Core components
│   ├── scraper.py         # BSE web scraper
│   ├── processor.py       # Data processor
│   └── excel_generator.py # Excel export
├── quantum/               # Quantum suite modules
│   ├── scrapers/          # NSE/BSE scrapers
│   ├── services/          # Business logic
│   ├── exporters/         # Export handlers
│   └── ui/                # UI components
├── utils/                 # Utility functions
│   ├── models.py          # Data models
│   ├── persistence.py     # Config persistence
│   └── stock_list.py      # Stock symbols
├── tests/                 # Test files
└── .streamlit/            # Streamlit config
    └── config.toml        # Theme settings
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_processor.py

# Run with coverage
pytest --cov=components --cov=quantum
```

---

## Troubleshooting

### Chrome/Selenium Issues

**Local Development:**
- Ensure Chrome is installed
- Update Chrome to latest version
- The app auto-downloads ChromeDriver

**Streamlit Cloud:**
- Chrome binary paths are pre-configured
- `packages.txt` installs Chromium automatically

### Module Not Found

```bash
pip install -r requirements.txt
```

### Port Already in Use

```bash
# Kill existing Streamlit process
# Windows:
taskkill /F /IM streamlit.exe

# macOS/Linux:
pkill -f streamlit

# Then restart
streamlit run app.py
```

### Permission Denied (Linux/Mac)

```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

---

## Configuration

### Environment Variables (Optional)

Create a `.env` file for custom settings:
```env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
```

### Streamlit Secrets (Cloud)

For sensitive data on Streamlit Cloud:
1. Go to app dashboard
2. Click "Settings" → "Secrets"
3. Add your secrets in TOML format

---

## Quick Commands Reference

| Command | Description |
|---------|-------------|
| `streamlit run app.py` | Start the app |
| `streamlit run app.py --server.port 8080` | Custom port |
| `pytest` | Run tests |
| `pip freeze > requirements.txt` | Update dependencies |
| `git push origin main` | Deploy updates |

---

## Support

- 📚 **Docs:** https://docs.streamlit.io/
- 💬 **Forum:** https://discuss.streamlit.io/
- 🐛 **Issues:** https://github.com/unknowncoder84/BSEwork/issues

---

**Happy Trading! 📈**
