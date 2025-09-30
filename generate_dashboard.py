import sys
sys.path.insert(0, '/project/workspace')
from src.database import get_db_context, Strategy, Backtest
from datetime import datetime

# Get data
with get_db_context() as db:
    strategies = db.query(Strategy).all()
    backtests = db.query(Backtest).order_by(Backtest.sharpe_ratio.desc()).all()

# Top 10 by Sharpe
top_backtests = [b for b in backtests if b.sharpe_ratio][:10]

html = f"""<!DOCTYPE html>
<html>
<head>
<title>Trading Agent Dashboard</title>
<style>
body {{ font-family: Arial; margin: 20px; background: #f5f5f5; }}
.header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
.stats {{ display: flex; gap: 20px; margin: 20px 0; }}
.stat-box {{ background: white; padding: 20px; border-radius: 5px; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
.stat-number {{ font-size: 36px; font-weight: bold; color: #3498db; }}
table {{ width: 100%; background: white; border-collapse: collapse; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
th {{ background: #34495e; color: white; padding: 12px; text-align: left; }}
td {{ padding: 12px; border-bottom: 1px solid #ddd; }}
tr:hover {{ background: #f8f9fa; }}
.positive {{ color: #27ae60; font-weight: bold; }}
.negative {{ color: #e74c3c; font-weight: bold; }}
</style>
</head>
<body>

<div class="header">
<h1>🤖 Trading Agent Dashboard</h1>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</div>

<div class="stats">
<div class="stat-box">
<div>Total Strategies</div>
<div class="stat-number">{len(strategies)}</div>
</div>
<div class="stat-box">
<div>Total Backtests</div>
<div class="stat-number">{len(backtests)}</div>
</div>
<div class="stat-box">
<div>Best Sharpe</div>
<div class="stat-number">{top_backtests[0].sharpe_ratio:.2f if top_backtests else 'N/A'}</div>
</div>
</div>

<h2>🏆 Top 10 Strategies by Sharpe Ratio</h2>
<table>
<tr>
<th>Rank</th>
<th>Strategy</th>
<th>Asset</th>
<th>Sharpe Ratio</th>
<th>Total Return</th>
<th>Win Rate</th>
<th>Max Drawdown</th>
</tr>
"""

for i, b in enumerate(top_backtests, 1):
    ret_class = 'positive' if (b.total_return or 0) > 0 else 'negative'
    html += f"""<tr>
<td>{i}</td>
<td>{b.strategy.name}</td>
<td>{b.symbol}</td>
<td>{b.sharpe_ratio:.2f}</td>
<td class="{ret_class}">{(b.total_return or 0)*100:.2f}%</td>
<td>{(b.win_rate or 0)*100:.1f}%</td>
<td class="negative">{(b.max_drawdown or 0)*100:.2f}%</td>
</tr>"""

html += """
</table>

<h2>📊 All Strategies</h2>
<table>
<tr><th>#</th><th>Strategy Name</th><th>Category</th><th>Created</th></tr>
"""

for i, s in enumerate(strategies, 1):
    html += f"""<tr>
<td>{i}</td>
<td>{s.name}</td>
<td>{s.category or 'N/A'}</td>
<td>{s.created_at.strftime('%Y-%m-%d %H:%M') if s.created_at else 'N/A'}</td>
</tr>"""

html += """
</table>

<div style="margin-top: 40px; padding: 20px; background: white; border-radius: 5px;">
<p><strong>🎯 Agent Status:</strong> Running 24/7</p>
<p><strong>📝 Note:</strong> Refresh this page anytime by running: <code>python generate_dashboard.py</code></p>
</div>

</body>
</html>
"""

with open('dashboard.html', 'w') as f:
    f.write(html)

print("✅ Dashboard created: dashboard.html")
print("📂 Download it and open in your browser!")
