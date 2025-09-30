# ⚡ Quick Deploy - 5 Minutes to 24/7 Operation

## 🎯 FASTEST OPTION: Railway (Recommended!)

### Step 1: Install Railway CLI (30 seconds)
```bash
npm install -g @railway/cli
```
Or without npm:
```bash
curl -fsSL https://railway.app/install.sh | sh
```

### Step 2: Login (30 seconds)
```bash
railway login
```
(Opens browser to login)

### Step 3: Deploy (2 minutes)
```bash
# From project directory
railway init
railway up
```

### Step 4: Get Your Dashboard URL (10 seconds)
```bash
railway domain
```

### ✅ DONE! 
Visit your URL - agent is running 24/7! 🎉

---

## 📱 Access Your Dashboard:

Your dashboard is now live at:
```
https://your-app.up.railway.app
```

You can access it:
- ✅ From your phone
- ✅ From any computer
- ✅ From anywhere in the world
- ✅ Even when your PC is OFF!

---

## 🔄 What's Running 24/7:

1. **Autonomous Agent**: Discovering strategies every hour
2. **Dashboard Updater**: Refreshing data every 5 seconds
3. **Web Server**: Serving your dashboard publicly

---

## 📊 Monitor Progress:

Just open your dashboard URL to see:
- Strategies discovered
- Backtests completed
- Performance metrics
- Real-time updates!

---

## 💰 Cost:

Railway gives you **$5/month FREE credit**!
This covers the basic agent with no payment needed initially.

---

## 🆘 If Railway Doesn't Work:

Try **DigitalOcean** ($200 free credit):

```bash
# 1. Sign up: https://www.digitalocean.com/
# 2. Create Droplet (Ubuntu, $4/month)
# 3. SSH into it
# 4. Run:

curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

git clone YOUR_REPO_URL
cd trading-agent
docker-compose -f docker-compose.cloud.yml up -d
```

Access at: `http://your-droplet-ip:8080`

---

## 🚀 That's It!

Your autonomous trading agent is now running 24/7 in the cloud!

**No PC needed. Access from anywhere. Always working.** 🎯
