# 🎯 Dashboard Access Guide

## ✅ Your Dashboard is LIVE!

The Trading Platform Dashboard is currently running and ready to access.

---

## 🌐 How to Access

### Method 1: VS Code / GitHub Codespaces (Recommended)

1. **Look for the PORTS tab** in your bottom panel (next to TERMINAL, PROBLEMS, etc.)
2. **Find port 8501** in the list
3. **Click the globe icon** (🌐) or "Open in Browser" button
4. The dashboard will open in your browser!

```
┌─────────────────────────────────────────┐
│ PORT    ADDRESS         VISIBILITY      │
│ 8501    0.0.0.0:8501   Public          │  ← Click here
└─────────────────────────────────────────┘
```

### Method 2: Direct URL (if port forwarding is set up)

```
http://localhost:8501
```

---

## 📊 What You'll See

### Dashboard Tabs

#### 📊 **Overview Tab**
- Total strategies count
- Total backtests count  
- Completed backtests count
- Scraped content items
- Average Sharpe Ratio
- Recent strategies feed
- Recent backtests feed

#### 💡 **Strategies Tab**
- Complete list of all trading strategies
- Strategy details (name, category, status, created date)
- Filter and search capabilities
- Detailed view with parameters
- Source URL links
- Description and metadata

#### 📈 **Backtests Tab**
- All completed backtest results
- Performance metrics table:
  - Total Return
  - Sharpe Ratio
  - Maximum Drawdown
  - Win Rate
  - Total Trades
- **Interactive Plotly Charts**:
  - Sharpe Ratio comparison bar chart
  - Performance visualizations
- Sortable and filterable data

#### 🌐 **Scraped Content Tab**
- All discovered trading content
- Filter by processed/unprocessed status
- Content preview (first 500 chars)
- Source URLs with links
- Scraping timestamp
- Strategy creation status

---

## 🎨 Dashboard Features

✅ **Real-time updates** - Refresh to see latest data  
✅ **Interactive charts** - Plotly.js powered visualizations  
✅ **Professional metrics** - Industry-standard performance indicators  
✅ **Responsive layout** - Works on desktop and tablet  
✅ **Dark/Light themes** - Streamlit's built-in theme support  
✅ **Filterable tables** - Easy data exploration  
✅ **Expandable sections** - Organized information display  

---

## 📈 Adding More Data

Run demos to populate the dashboard with more results:

```bash
# Test multiple assets
python demo_1_multiple_stocks.py

# Create custom strategies
python demo_2_custom_strategy.py

# Optimize parameters
python demo_3_parameter_optimization.py

# Scrape web content
python demo_4_web_scraping.py

# Quick backtest demo
python quick_backtest_demo.py
```

After running any demo, **just refresh your browser** to see the new data!

---

## 🔄 Dashboard Controls

### Sidebar Options:
- **Refresh Interval Slider**: Set auto-refresh timing (5-60 seconds)
- **🔄 Refresh Data Button**: Manual refresh trigger
- **🌐 Run Web Search**: Trigger web scraping (coming soon)
- **🤖 Start Scheduler**: Enable automation (coming soon)

---

## 🚀 Advanced: Running the API

For programmatic access, you can also run the FastAPI backend:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Then access:
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 📊 Current Database Stats

```
Strategies: 1
Backtests: 1 completed
Scraped Content: 10 items
```

---

## 🛠️ Troubleshooting

### Dashboard not loading?

1. **Check if Streamlit is running**:
   ```bash
   ps aux | grep streamlit
   ```

2. **Restart the dashboard**:
   ```bash
   pkill -f streamlit
   streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
   ```

3. **Check logs**:
   ```bash
   tail -f /tmp/streamlit.log
   ```

### Port already in use?

```bash
# Find and kill process on port 8501
lsof -ti:8501 | xargs kill -9

# Then restart
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

---

## 💡 Pro Tips

1. **Run demos in the background** while viewing dashboard - see updates in real-time!
2. **Use the API** for automated testing and data retrieval
3. **Check the PORTS tab** frequently - it shows connection status
4. **Refresh often** after running demos to see new results
5. **Use sidebar filters** to focus on specific data

---

## 🎯 Next Steps

Now that your dashboard is running:

1. ✅ **Access the dashboard** using the PORTS tab
2. 📊 **Explore the current data** in all 4 tabs
3. 🚀 **Run more demos** to add diverse data
4. 📈 **Watch the charts update** as you add backtests
5. 🔍 **Use the filters** to analyze specific strategies
6. 🌐 **Start the API** for programmatic access (optional)

---

**Dashboard Status**: ✅ **RUNNING ON PORT 8501**

**Process ID**: Check with `ps aux | grep streamlit`

**Log File**: `/tmp/streamlit.log`

---

Enjoy your world-class trading platform dashboard! 🎉
