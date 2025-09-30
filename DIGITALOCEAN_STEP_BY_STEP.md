# 🌊 DigitalOcean Deployment - Complete Step by Step Guide

## ✅ What You'll Get:
- 24/7 running agent (even when PC is off)
- Public dashboard URL (access from anywhere)
- $200 FREE credit (covers 50 days!)
- Everything done in browser!

---

## 📋 PART 1: Create DigitalOcean Account (2 minutes)

### Step 1: Sign Up

1. Go to: **https://www.digitalocean.com/**
2. Click **"Sign Up"** (top right)
3. Use Google/GitHub login OR email
4. Verify your email

### Step 2: Add Payment Method

**Don't worry!** You get **$200 FREE credit** for 60 days!

1. Click "Billing" → "Payment Methods"
2. Add credit card OR PayPal
3. You won't be charged for 60 days!
4. See "$200.00 credit" in your account

---

## 📋 PART 2: Create Your Server (Droplet) (3 minutes)

### Step 1: Create Droplet

1. Click green **"Create"** button (top right)
2. Select **"Droplets"**

### Step 2: Choose Options

**Image:**
- Select: **Ubuntu 22.04 (LTS) x64**

**Droplet Size:**
- Click "Basic" plan
- Select: **Regular - $4/mo** 
  (1 GB RAM, 25 GB SSD - perfect for us!)

**Datacenter Region:**
- Choose closest to you
  - New York (if in USA East)
  - San Francisco (if in USA West)
  - London (if in Europe)
  - Frankfurt (if in Europe)

**Authentication:**
- Select: **"Password"**
- Create a strong password (save it!)

**Hostname:**
- Name it: `trading-agent` (or whatever you want)

### Step 3: Create!

1. Click green **"Create Droplet"** button at bottom
2. Wait 30 seconds while it creates
3. You'll see your droplet with an **IP address** like: `123.45.67.89`

**COPY THIS IP ADDRESS!** You'll need it!

---

## 📋 PART 3: Access Your Server (1 minute)

### Step 1: Open Console

1. Click on your droplet name
2. Click **"Console"** button (top right)
3. A browser terminal opens! (no SSH needed!)

### Step 2: Login

1. Type: `root`
2. Press Enter
3. Paste your password (right-click to paste)
4. Press Enter

You're in! You'll see: `root@trading-agent:~#`

---

## 📋 PART 4: Deploy Your Trading Agent (5 minutes)

### Now just COPY and PASTE these commands!

Each command block - copy ALL of it, paste in console, press Enter!

---

### Command 1: Update System

```bash
apt update && apt upgrade -y
```

**Wait:** 1-2 minutes
**You'll see:** Lots of text scrolling, then `root@trading-agent:~#` again

---

### Command 2: Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
```

**Wait:** 1-2 minutes
**You'll see:** Docker installation messages

---

### Command 3: Install Docker Compose

```bash
apt install docker-compose -y
```

**Wait:** 30 seconds

---

### Command 4: Create Project Directory

```bash
mkdir -p /root/trading-agent && cd /root/trading-agent
```

**Instant!** No output = success!

---

### Command 5: Download Project Files

```bash
cat > docker-compose.yml << 'COMPOSE_EOF'
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
      pip install --no-cache-dir yfinance pandas numpy sqlalchemy pydantic pydantic-settings requests duckduckgo-search beautifulsoup4 lxml optuna scikit-learn fastapi uvicorn streamlit apscheduler ccxt &&
      python -c 'from src.research_agent import ResearchAgent; ResearchAgent().run_forever(3600)' &
      python update_dashboard_data.py &
      sleep infinity
      "
    restart: always
    environment:
      - DATABASE_URL=sqlite:///./data/trading_agent.db

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

volumes:
  data:
COMPOSE_EOF
```

**You'll see:** Nothing = good!

---

### Command 6: Create Application Directory

```bash
mkdir -p app/src
```

---

### Command 7: Download All Source Code

This is the BIG one - creates all your Python code!

```bash
# I'll provide the complete code in the next message
# because it's very long!
```

**WAIT!** I'll give you the complete code to paste in the next step!

---

## 📋 NEXT STEPS:

After you complete the above commands, tell me and I'll give you:

1. **The full source code** to paste (creates all your agent files)
2. **Start command** to launch everything
3. **Your dashboard URL** to access!

---

## 🎯 WHERE ARE YOU NOW?

Tell me which step you're on:
- [ ] Created DigitalOcean account
- [ ] Created Droplet
- [ ] Opened Console
- [ ] Ready to paste commands

**What step are you on?** 🚀
