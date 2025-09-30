# 🚀 24/7 Cloud Deployment Guide

Run your autonomous trading agent 24/7 in the cloud, even when your PC is off!

## 📋 What Will Run 24/7:
- ✅ Autonomous Research Agent (discovers strategies, optimizes, tests)
- ✅ Dashboard Data Updater (updates every 5 seconds)
- ✅ Web Dashboard (accessible from anywhere)

---

## 🎯 OPTION 1: Railway (Easiest - FREE Tier Available)

### Why Railway?
- ✅ Free $5/month credit
- ✅ Super easy deployment
- ✅ No credit card needed initially
- ✅ Auto-restarts if crashes
- ✅ Public URL for dashboard

### Steps:

1. **Create Account**: https://railway.app/

2. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   # OR
   curl -fsSL https://railway.app/install.sh | sh
   ```

3. **Login**:
   ```bash
   railway login
   ```

4. **Deploy from this directory**:
   ```bash
   railway init
   railway up
   ```

5. **Set Environment Variables**:
   ```bash
   railway variables set DATABASE_URL=sqlite:///./data/trading_agent.db
   ```

6. **Expose Dashboard**:
   - Go to Railway dashboard
   - Click your service → Settings → Generate Domain
   - Your dashboard will be at: `https://your-app.up.railway.app`

**Cost**: FREE for small projects (~$5/month credit covers it!)

---

## 🎯 OPTION 2: Render (Great Free Tier)

### Why Render?
- ✅ Free tier available
- ✅ Auto-deploy from GitHub
- ✅ Simple dashboard
- ✅ SSL/HTTPS included

### Steps:

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/trading-agent.git
   git push -u origin main
   ```

2. **Create Account**: https://render.com/

3. **Create New Web Service**:
   - Connect your GitHub repo
   - Choose "Docker"
   - Use `docker-compose.cloud.yml`

4. **Configure**:
   - Instance Type: Free
   - Docker Command: Leave default
   - Add environment variables

5. **Deploy**: Click "Create Web Service"

**Cost**: FREE tier available!

---

## 🎯 OPTION 3: AWS EC2 (Most Control)

### Why AWS?
- ✅ 12 months free tier
- ✅ Full control
- ✅ Scalable
- ✅ Professional solution

### Steps:

1. **Launch EC2 Instance**:
   - t2.micro (free tier)
   - Ubuntu 22.04 LTS
   - Open ports: 8080 (dashboard)

2. **SSH into instance**:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Install Docker**:
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose
   sudo usermod -aG docker ubuntu
   ```

4. **Clone and Deploy**:
   ```bash
   git clone YOUR_REPO_URL
   cd trading-agent
   docker-compose -f docker-compose.cloud.yml up -d
   ```

5. **Access Dashboard**:
   - http://your-ec2-ip:8080

**Cost**: FREE for 12 months, then ~$10/month

---

## 🎯 OPTION 4: DigitalOcean (Easiest VPS)

### Why DigitalOcean?
- ✅ $200 free credit for 60 days
- ✅ Simple interface
- ✅ Good documentation

### Steps:

1. **Create Account**: https://www.digitalocean.com/ (use referral for $200 credit)

2. **Create Droplet**:
   - Ubuntu 22.04
   - Basic plan: $4/month (covered by free credit!)
   - Choose region closest to you

3. **SSH and Install**:
   ```bash
   ssh root@your-droplet-ip
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Clone repo
   git clone YOUR_REPO_URL
   cd trading-agent
   
   # Run
   docker-compose -f docker-compose.cloud.yml up -d
   ```

4. **Access Dashboard**: http://your-droplet-ip:8080

**Cost**: $4/month (FREE for 2 months with credit!)

---

## 🎯 OPTION 5: Google Cloud Run (Serverless)

### Why Cloud Run?
- ✅ $300 free credit
- ✅ Pay only for usage
- ✅ Auto-scales
- ✅ Very cheap for small projects

### Steps:

1. **Install gcloud CLI**: https://cloud.google.com/sdk/docs/install

2. **Build and Deploy**:
   ```bash
   gcloud run deploy trading-agent \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

3. **Access**: URL provided after deployment

**Cost**: FREE tier covers most small projects!

---

## 🎯 OPTION 6: Heroku (Simple but Paid)

### Why Heroku?
- ✅ Super simple
- ✅ Good documentation
- ✅ Reliable

### Steps:

1. **Install Heroku CLI**:
   ```bash
   npm install -g heroku
   ```

2. **Deploy**:
   ```bash
   heroku login
   heroku create your-app-name
   heroku stack:set container
   git push heroku main
   ```

**Cost**: ~$7/month (no free tier anymore)

---

## 📊 Recommended Choice by Use Case:

| Use Case | Best Option | Why |
|----------|-------------|-----|
| **Easiest & Free** | Railway | Zero config, free tier, instant deploy |
| **GitHub Integration** | Render | Auto-deploy from GitHub, free SSL |
| **Learning Cloud** | AWS EC2 | 12 months free, learn real cloud |
| **Best Value** | DigitalOcean | $200 credit, simple, $4/month after |
| **Serverless** | Google Cloud Run | Cheapest for intermittent use |
| **Professional** | AWS/GCP | Scalable, enterprise-ready |

---

## 🔧 What Runs 24/7:

### 1. Autonomous Agent
- Searches web for strategies every hour
- Creates new strategies automatically
- Optimizes parameters
- Backtests on multiple assets
- **Never stops!**

### 2. Dashboard Updater
- Updates dashboard_data.json every 5 seconds
- Pulls fresh data from database
- Keeps dashboard live

### 3. Web Server
- Serves your dashboard on public URL
- Accessible from any device
- Auto-updates every 5 seconds

---

## 📱 Accessing Your Dashboard:

Once deployed, you can access your dashboard:
- **From your phone** 📱
- **From work** 💼
- **From anywhere** 🌍

Just visit: `http://your-server-url:8080`

---

## 💰 Cost Summary:

| Platform | Free Credit | Monthly Cost | Best For |
|----------|-------------|--------------|----------|
| Railway | $5/month | $0-5 | Beginners |
| Render | Free tier | $0 | GitHub users |
| AWS EC2 | 12 months free | $10 | Learning |
| DigitalOcean | $200 (60 days) | $4 | Best value |
| Google Cloud | $300 | $0-5 | Serverless |

---

## 🚀 Quick Start (Railway - Easiest):

```bash
# 1. Install Railway
npm install -g @railway/cli

# 2. Login
railway login

# 3. Deploy (from project directory)
railway init
railway up

# 4. Get URL
railway domain

# 5. Done! Visit your URL to see dashboard
```

**Your agent is now running 24/7! 🎉**

---

## 📊 Monitoring Your Agent:

Check progress anytime:
- Visit your dashboard URL
- See strategies discovered
- View backtest results
- Monitor performance

**All updated in real-time, even from your phone!**

---

## 🔄 Updating Your Deployment:

When you make changes:

```bash
# Push changes
git add .
git commit -m "Update agent"
git push

# Railway/Render auto-deploy!
# For manual deployments:
railway up  # Railway
# OR
docker-compose -f docker-compose.cloud.yml up -d --build  # Docker
```

---

## 🎯 Need Help?

Choose **Railway** if you want the easiest setup!
Choose **DigitalOcean** if you want best value!
Choose **AWS** if you want to learn cloud!

**All options keep your agent running 24/7, even when your PC is off!** 🚀
