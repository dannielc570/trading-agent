#!/bin/bash
# DigitalOcean Deployment Script
# Paste this entire script into DigitalOcean console!

set -e

echo "🚀 Starting Trading Agent Deployment..."
echo ""

# Step 1: Update system
echo "📦 Step 1/8: Updating system..."
apt update && apt upgrade -y

# Step 2: Install Docker
echo "🐋 Step 2/8: Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Step 3: Install Docker Compose
echo "🔧 Step 3/8: Installing Docker Compose..."
apt install docker-compose -y

# Step 4: Create directories
echo "📁 Step 4/8: Creating project directories..."
mkdir -p /root/trading-agent/{app/src/{research_agent,backtesting,data_collection,database,ml_optimization},data}
cd /root/trading-agent

# Step 5: Create requirements.txt
echo "📋 Step 5/8: Creating requirements..."
cat > app/requirements.txt << 'EOF'
yfinance>=0.2.28
pandas>=2.0.0
numpy>=1.24.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
requests>=2.31.0
duckduckgo-search>=3.8.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
optuna>=3.3.0
scikit-learn>=1.3.0
fastapi>=0.100.0
uvicorn>=0.23.0
streamlit>=1.25.0
apscheduler>=3.10.0
ccxt>=4.0.0
EOF

# Step 6: Create dashboard files
echo "🎨 Step 6/8: Creating dashboard..."
cat > app/live_dashboard.html << 'HTMLEOF'
<!DOCTYPE html>
<html>
<head>
<title>Live Trading Agent Dashboard</title>
<meta charset="UTF-8">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; padding: 20px; }
.container { max-width: 1400px; margin: 0 auto; }
.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.header h1 { font-size: 32px; margin-bottom: 10px; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
.stat-card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.stat-value { font-size: 36px; font-weight: bold; color: #2d3748; }
.section { background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
table { width: 100%; border-collapse: collapse; }
th { background: #4a5568; color: white; padding: 12px; text-align: left; }
td { padding: 12px; border-bottom: 1px solid #e2e8f0; }
.auto-refresh { position: fixed; bottom: 20px; right: 20px; background: #48bb78; color: white; padding: 12px 20px; border-radius: 25px; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🤖 Live Trading Agent Dashboard</h1>
    <div>Last Updated: <span id="last-updated">Loading...</span></div>
  </div>
  <div class="stats">
    <div class="stat-card">
      <div>Total Strategies</div>
      <div class="stat-value" id="total-strategies">-</div>
    </div>
    <div class="stat-card">
      <div>Total Backtests</div>
      <div class="stat-value" id="total-backtests">-</div>
    </div>
    <div class="stat-card">
      <div>Best Sharpe Ratio</div>
      <div class="stat-value" id="best-sharpe">-</div>
    </div>
  </div>
  <div class="section">
    <h2>🏆 Top Strategies</h2>
    <table>
      <thead><tr><th>Strategy</th><th>Asset</th><th>Sharpe</th><th>Return</th></tr></thead>
      <tbody id="top-backtests"><tr><td colspan="4">Loading...</td></tr></tbody>
    </table>
  </div>
</div>
<div class="auto-refresh">🔄 Auto-Refreshing</div>
<script>
async function loadDashboardData() {
  try {
    const response = await fetch('dashboard_data.json?t=' + Date.now());
    const data = await response.json();
    document.getElementById('last-updated').textContent = data.last_updated;
    document.getElementById('total-strategies').textContent = data.stats.total_strategies;
    document.getElementById('total-backtests').textContent = data.stats.total_backtests;
    document.getElementById('best-sharpe').textContent = data.stats.best_sharpe.toFixed(2);
    const html = data.top_backtests.map(b => 
      `<tr><td>${b.strategy}</td><td>${b.asset}</td><td>${b.sharpe.toFixed(2)}</td><td>${b.return.toFixed(2)}%</td></tr>`
    ).join('');
    document.getElementById('top-backtests').innerHTML = html || '<tr><td colspan="4">No data yet</td></tr>';
  } catch (e) { console.error(e); }
}
loadDashboardData();
setInterval(loadDashboardData, 5000);
</script>
</body>
</html>
HTMLEOF

cat > app/update_dashboard_data.py << 'PYEOF'
import json
import time
from datetime import datetime

def create_sample_data():
    return {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stats": {"total_strategies": 0, "total_backtests": 0, "best_sharpe": 0},
        "top_backtests": []
    }

while True:
    try:
        with open('/app/data/dashboard_data.json', 'w') as f:
            json.dump(create_sample_data(), f)
        time.sleep(5)
    except:
        time.sleep(5)
PYEOF

# Step 7: Create minimal source structure
echo "🏗️  Step 7/8: Creating source code structure..."
touch app/src/__init__.py
mkdir -p app/src/research_agent
touch app/src/research_agent/__init__.py
cat > app/src/research_agent/main_agent.py << 'AGENTEOF'
import time
from datetime import datetime

class ResearchAgent:
    def __init__(self):
        print(f"{datetime.now()} | INFO | 🤖 Research Agent initialized")
    
    def run_forever(self, interval=3600):
        print(f"{datetime.now()} | INFO | 🚀 Starting 24/7 operation (interval: {interval}s)")
        cycle = 0
        while True:
            try:
                cycle += 1
                print(f"{datetime.now()} | INFO | 🔄 Cycle #{cycle} started")
                # Agent logic would go here
                print(f"{datetime.now()} | INFO | ✅ Cycle #{cycle} completed")
            except Exception as e:
                print(f"{datetime.now()} | ERROR | {e}")
            time.sleep(interval)
AGENTEOF

# Step 8: Create docker-compose
echo "🐳 Step 8/8: Creating Docker Compose configuration..."
cat > docker-compose.yml << 'COMPOSEEOF'
version: '3.8'

services:
  agent:
    image: python:3.10-slim
    container_name: trading-agent
    working_dir: /app
    volumes:
      - ./app:/app
      - ./data:/app/data
    command: >
      bash -c "
      pip install --no-cache-dir yfinance pandas numpy sqlalchemy pydantic pydantic-settings requests beautifulsoup4 lxml &&
      python -c 'import sys; sys.path.insert(0, \"/app\"); from src.research_agent.main_agent import ResearchAgent; ResearchAgent().run_forever(3600)' &
      python /app/update_dashboard_data.py &
      tail -f /dev/null
      "
    restart: always

  webserver:
    image: nginx:alpine
    container_name: dashboard-server
    ports:
      - "8080:80"
    volumes:
      - ./app/live_dashboard.html:/usr/share/nginx/html/index.html:ro
      - ./data/dashboard_data.json:/usr/share/nginx/html/dashboard_data.json:ro
    restart: always
    depends_on:
      - agent
COMPOSEEOF

# Step 9: Start everything!
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "📊 Your dashboard is available at:"
echo "   http://$(curl -s ifconfig.me):8080"
echo ""
echo "🎉 Agent is running 24/7!"
echo ""
echo "Check logs: docker-compose logs -f"
