# 🏠 Run Trading Platform on Your Local PC

## Why localhost:8501 doesn't work

The dashboard is running on Factory.ai's **remote server**, not your PC. When you type `http://localhost:8501` in your browser, it looks for something running on YOUR computer - but nothing is there!

## ✅ Solution: Run Everything Locally

Follow these simple steps to get it running on your PC:

---

## 📋 Prerequisites

- **Python 3.9 or higher** ([Download here](https://www.python.org/downloads/))
- **Git** (optional, for cloning)
- **10 minutes of time**

---

## 🚀 Quick Setup (5 Steps)

### Step 1: Create Project Folder

Open Terminal (Mac/Linux) or Command Prompt (Windows):

```bash
# Create folder
mkdir trading-platform
cd trading-platform
```

### Step 2: Get the Code

**Option A: Download from Factory.ai**

1. In Factory.ai workspace, look for a "Download" or "Export" option
2. Download the entire project folder
3. Extract to your `trading-platform` folder

**Option B: Clone from Git** (if you pushed to GitHub)

```bash
git clone YOUR_REPO_URL .
```

**Option C: I'll create a setup script for you!** (see below)

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install pandas numpy yfinance requests beautifulsoup4 sqlalchemy pydantic-settings fastapi uvicorn streamlit plotly duckduckgo-search ccxt apscheduler scikit-learn
```

Or if you have the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Dashboard

```bash
streamlit run src/dashboard/app.py
```

### Step 5: Open Your Browser

The dashboard will automatically open at:

```
http://localhost:8501
```

**NOW it will work because it's running on YOUR computer!** 🎉

---

## 🤖 Run the Autonomous Agent

Once setup is complete:

```bash
# Run demo
python demo_autonomous_agent.py

# Run 24/7
python -c "from src.research_agent import ResearchAgent; ResearchAgent().run_forever(3600)"
```

---

## 📦 Complete Project Structure

Your folder should look like this:

```
trading-platform/
├── src/
│   ├── data_collection/
│   ├── backtesting/
│   ├── ml_optimization/
│   ├── research_agent/     ← Autonomous agent
│   ├── api/
│   ├── dashboard/          ← Website
│   ├── database/
│   └── scheduler/
├── demo_1_multiple_stocks.py
├── demo_2_custom_strategy.py
├── demo_3_parameter_optimization.py
├── demo_4_web_scraping.py
├── demo_autonomous_agent.py
├── requirements.txt
└── README.md
```

---

## 🔧 Troubleshooting

### "Python not found"
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### "pip not found"
- Use `python -m pip install ...` instead of `pip install ...`

### "Module not found" errors
- Run: `pip install -r requirements.txt` again
- Or install missing packages individually: `pip install package_name`

### Port 8501 already in use
- Change port: `streamlit run src/dashboard/app.py --server.port 8502`
- Then use: http://localhost:8502

---

## 📥 Download Files from Remote Workspace

If you can't download the whole project, I can create a setup script that will recreate everything!

Just let me know and I'll generate a single Python script that:
1. Creates all folders
2. Downloads all dependencies
3. Sets up the database
4. Runs the dashboard

---

## 🎯 What You'll Get

Once running locally, you'll have:

✅ **Web Dashboard** at http://localhost:8501
- Overview with stats
- Strategy list
- Interactive backtest charts
- Scraped content

✅ **Autonomous Agent** running 24/7
- Discovers strategies
- Optimizes parameters
- Tests on multiple assets
- Learns and improves

✅ **Full Control** on your own machine
- No remote dependencies
- All data stored locally
- Run anytime, anywhere

---

## 🚀 Next Steps

1. Follow the setup steps above
2. Run the dashboard: `streamlit run src/dashboard/app.py`
3. Run some demos to populate data
4. Start the autonomous agent!

**Questions? Let me know what step you're on and I'll help!**
