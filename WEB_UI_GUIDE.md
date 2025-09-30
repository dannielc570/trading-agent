# 🌐 Trading Platform Web UI

## 🚀 World-Class Dashboard

A **beautiful, modern web interface** to view all your trading strategies, backtests, stats, and charts!

### ✨ Features

- **📊 Real-time Stats Dashboard**
  - Total strategies tracked
  - Backtests completed
  - Best performing strategy
  - Average Sharpe ratio

- **🏆 Strategy Leaderboard**
  - Rankings by performance
  - Category badges
  - Test counts
  - Interactive sorting

- **📈 Interactive Charts**
  - Performance visualizations
  - Color-coded returns (green = profit, red = loss)
  - Hover tooltips with details

- **💰 Asset Performance Comparison**
  - Average returns by asset
  - Number of tests per asset
  - Quick performance overview

- **📋 Recent Backtests Table**
  - Full metrics (Return, Sharpe, Drawdown, Win Rate)
  - Strategy and asset details
  - Status indicators

- **🔄 Auto-Refresh**
  - Updates every 30 seconds
  - Manual refresh button
  - Live data monitoring

---

## 🎯 How to Access

###  1. Start the Web Server

```bash
python run_website.py
```

### 2. Open Your Browser

Navigate to: **http://localhost:8080**

The dashboard will load automatically!

---

## 🎨 What You'll See

### Top Stats Cards
- **Total Strategies**: Number of strategies discovered and created
- **Backtests Run**: Total tests with completed count
- **Best Return**: Highest performing strategy with percentage
- **Avg Sharpe Ratio**: Risk-adjusted performance metric

### Strategy Leaderboard
Beautiful table showing:
- Strategy name and category
- Best return percentage (color-coded badges)
- Sharpe ratio
- Number of backtests run

### Asset Performance
Comparison table of:
- Asset symbols (AAPL, BTC-USD, etc.)
- Average returns across all tests
- Test counts

### Interactive Chart
Bar chart visualization of recent backtests:
- Green bars = profitable
- Red bars = unprofitable
- Hover for detailed info

### Recent Backtests
Complete table with all metrics:
- Strategy name
- Asset symbol
- Total return %
- Sharpe ratio
- Maximum drawdown %
- Win rate %
- Number of trades

---

## 📡 API Endpoints

The server also provides REST API endpoints:

- `GET /` - Main dashboard (HTML)
- `GET /api/stats` - Platform statistics (JSON)
- `GET /api/strategies` - All strategies with performance (JSON)
- `GET /api/backtests?limit=50` - Recent backtests (JSON)
- `GET /api/performance-chart` - Chart data (JSON)
- `GET /api/asset-comparison` - Asset performance data (JSON)
- `GET /docs` - Interactive API documentation

### Example API Call

```bash
curl http://localhost:8080/api/stats
```

```json
{
  "total_strategies": 7,
  "total_backtests": 42,
  "completed_backtests": 38,
  "total_scraped": 25,
  "best_strategy": "RSI Mean Reversion",
  "best_return": 26.62,
  "avg_return": 8.45,
  "avg_sharpe": 0.73
}
```

---

## 🎨 Design Features

### Modern UI
- Gradient purple background
- Clean white cards with shadows
- Smooth animations and hover effects
- Responsive design (mobile-friendly)

### Color Coding
- **Green badges**: Positive returns
- **Red badges**: Negative returns
- **Purple gradients**: Highlights and headers
- **Status dots**: Strategy status indicators

### Typography
- San Francisco / Segoe UI font stack
- Clear hierarchy with size variations
- Readable colors and contrast

### Charts
- Interactive with Chart.js
- Responsive canvas sizing
- Custom tooltips
- Color-coded bars

---

## 🔧 How It Works

### Backend (FastAPI)
- Python FastAPI server
- SQLAlchemy database queries
- JSON API responses
- Jinja2 template rendering

### Frontend (HTML/CSS/JS)
- Pure vanilla JavaScript (no framework needed)
- Chart.js for visualizations
- Fetch API for data loading
- CSS Grid and Flexbox layouts

### Auto-Refresh
- JavaScript `setInterval` calls API every 30s
- Manual refresh button available
- Non-blocking async loading

---

## 📊 Using with Demo Data

The dashboard shows real data from your database:

1. **Run some demos first:**
   ```bash
   python demo_1_multiple_stocks.py
   python demo_2_custom_strategy.py
   python demo_3_parameter_optimization.py
   ```

2. **Start the web UI:**
   ```bash
   python run_website.py
   ```

3. **Open browser:**
   Visit http://localhost:8080

4. **See your results!**
   - All strategies listed
   - Performance charts
   - Asset comparisons
   - Full backtest history

---

## 🚀 Production Deployment

For production use:

### Option 1: Docker

```bash
docker build -t trading-platform-ui -f Dockerfile .
docker run -p 8080:8080 trading-platform-ui
```

### Option 2: Systemd Service

Create `/etc/systemd/system/trading-ui.service`:

```ini
[Unit]
Description=Trading Platform Web UI
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/python run_website.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable trading-ui
sudo systemctl start trading-ui
```

### Option 3: Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🎯 Next Steps

1. ✅ **Current**: Beautiful web dashboard working
2. **Add authentication**: User login system
3. **Add strategy creation UI**: Build strategies in browser
4. **Add live trading controls**: Start/stop strategies
5. **Add notifications**: Email/Slack alerts for performance
6. **Add portfolio view**: Multi-strategy allocation
7. **Add parameter tuning UI**: Interactive optimization

---

## 💡 Tips

- **Data not showing?** Run the demo scripts first!
- **Port already in use?** Change port in `run_website.py`
- **Want HTTPS?** Use Nginx or Caddy reverse proxy
- **Need remote access?** Deploy to cloud (AWS, GCP, DigitalOcean)
- **Want mobile app?** The UI is already responsive!

---

## 🏆 Features Comparison

| Feature | Streamlit | Our Web UI |
|---------|-----------|------------|
| Design | Basic | **World-class** ✨ |
| Speed | Slow | **Fast** ⚡ |
| Customization | Limited | **Unlimited** 🎨 |
| Mobile | Poor | **Responsive** 📱 |
| Production-Ready | No | **Yes** 🚀 |
| API Access | No | **Yes** 📡 |

---

**Enjoy your beautiful trading platform dashboard!** 🎉
