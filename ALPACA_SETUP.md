# 🎉 GET YEARS OF 1-MINUTE DATA FOR FREE!

## Alpaca Data - Unlimited Historical Data

Alpaca provides **100% FREE** access to:
- ✅ **YEARS** of 1-minute historical data  
- ✅ All US stocks (NYSE, NASDAQ, etc.)
- ✅ Real-time quotes
- ✅ **NO rate limits** on historical data
- ✅ 10,000 bars per request

---

## 🚀 Setup (5 Minutes)

### Step 1: Sign Up (FREE)
1. Go to: **https://alpaca.markets/**
2. Click **"Sign Up"** (100% FREE)
3. Choose **"Paper Trading"** account (FREE, no real money needed)

### Step 2: Get API Keys
1. Log in to your Alpaca dashboard
2. Go to **"Paper Trading"** section
3. Click **"Generate API Keys"**
4. Copy **both** keys:
   - API Key ID
   - Secret Key

### Step 3: Add to Environment
Add these to your `.env` file (or Render environment variables):

```env
ALPACA_API_KEY=your_api_key_id_here
ALPACA_SECRET_KEY=your_secret_key_here
```

### Step 4: Restart Agent
Restart your trading agent, and it will automatically use Alpaca for 1-minute data!

---

## 📊 What You Get

### Data Coverage
- **Timeframes:** 1Min, 5Min, 15Min, 30Min, 1Hour, 1Day
- **History:** Up to **5+ years** of 1-minute data!
- **Assets:** All US stocks on major exchanges
- **Volume:** 10,000 bars per request (unlimited requests!)

### Example Usage
- **1 year** of 1-min data: **98,000+** bars per stock
- **2 years:** **196,000+** bars
- **5 years:** **490,000+** bars!

Perfect for **robust backtesting** across multiple years! 📈

---

## 🤖 How Your Agent Uses It

Once configured, your agent will:

1. **Automatically fetch** years of 1-minute data for all assets
2. **Backtest strategies** on 1-5 years of historical data
3. **Find optimal timeframes** using extensive data
4. **No more 7-day limitation!**

---

## ✅ Verification

Check your agent logs for:
```
✅ Alpaca data source available (FREE years of 1-min data!)
📊 Fetching 2 YEARS of 1Min data for AAPL...
✅ Total: 196,000 bars (2 years of 1Min data)
```

---

## 🆘 Troubleshooting

### "Alpaca not configured"
- Make sure you added API keys to `.env` file
- Restart your agent

### "Alpaca API error: 401"
- Check that API keys are correct
- Make sure you're using **Paper Trading** keys

### "No data returned"
- Make sure symbol is correct (e.g., 'AAPL' not 'AAPL.US')
- Check that market is open or use historical dates

---

## 🔗 Resources

- **Alpaca Documentation:** https://alpaca.markets/docs/
- **API Reference:** https://alpaca.markets/docs/api-references/market-data-api/
- **Support:** https://alpaca.markets/support/

---

**Now you have YEARS of data for FREE!** 🎉🚀
