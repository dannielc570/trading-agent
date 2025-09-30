# 🪟 Windows Deployment Guide - Step by Step

## 📋 BEFORE YOU START:

You need:
1. ✅ Project files downloaded to your PC
2. ✅ Node.js installed (for Railway CLI)

---

## STEP 1: Download Project Files

1. In Factory.ai, download ALL files to a folder on your PC
   Example: `C:\trading-agent\`

2. Make sure you have:
   - src/ folder
   - live_dashboard.html
   - dashboard_data.json
   - requirements.txt
   - Dockerfile.cloud
   - docker-compose.cloud.yml
   - etc.

---

## STEP 2: Install Node.js (If Not Installed)

### Check if you have it:
```cmd
node --version
```

If you see a version number (like v18.0.0), **SKIP TO STEP 3**!

If not installed:
1. Download from: https://nodejs.org/
2. Choose "LTS" version (recommended)
3. Run installer
4. Restart CMD after installation

---

## STEP 3: Open CMD in Project Folder

### Method 1: Easy Way
1. Open File Explorer
2. Go to your project folder (e.g., `C:\trading-agent\`)
3. Click in the address bar
4. Type `cmd` and press Enter
5. CMD opens in that folder!

### Method 2: Manual Way
```cmd
cd C:\trading-agent
```
(Replace with your actual path)

---

## STEP 4: Install Railway CLI

```cmd
npm install -g @railway/cli
```

**Wait for it to finish!** You'll see:
```
added 1 package
```

---

## STEP 5: Login to Railway

```cmd
railway login
```

**What happens:**
- Your browser opens
- Sign up/login with GitHub or email
- Browser says "Success!"
- Return to CMD

---

## STEP 6: Initialize Project

```cmd
railway init
```

**Answer the prompts:**
- Project name: `trading-agent` (or whatever you want)
- Press Enter

---

## STEP 7: Deploy!

```cmd
railway up
```

**Wait 2-3 minutes** while it:
- ✅ Uploads your code
- ✅ Builds Docker image
- ✅ Starts services

You'll see:
```
✓ Deployment successful
```

---

## STEP 8: Get Your Public URL

```cmd
railway domain
```

**You'll see:**
```
https://trading-agent-production-xxxx.up.railway.app
```

**COPY THIS URL!** This is your 24/7 dashboard! 🎉

---

## STEP 9: Open Dashboard

Paste the URL in your browser:
```
https://your-app.up.railway.app
```

**You'll see:**
- ✅ Live dashboard
- ✅ Auto-updating every 5 seconds
- ✅ Agent working 24/7!

---

## ✅ DONE!

Your agent is now running 24/7 in the cloud!
- Turn off your PC ✅
- Access from phone ✅
- Access from anywhere ✅

---

## 🆘 TROUBLESHOOTING:

### "npm is not recognized"
→ Node.js not installed or not in PATH
→ Solution: Install Node.js, restart CMD

### "railway is not recognized"
→ Railway CLI not installed
→ Solution: Run `npm install -g @railway/cli` again

### "No such file or directory"
→ CMD not in project folder
→ Solution: `cd C:\path\to\your\project`

### Railway says "Authentication required"
→ Need to login
→ Solution: `railway login`

---

## 🔄 UPDATING YOUR DEPLOYMENT:

When you make changes:

```cmd
cd C:\trading-agent
railway up
```

That's it! Changes deployed!

---

## 💰 COST:

Railway gives you **$5/month FREE credit**.
Your basic agent should run for FREE!

Monitor usage at: https://railway.app/dashboard

---

## 📱 ACCESS FROM PHONE:

Just open your Railway URL on your phone!
```
https://your-app.up.railway.app
```

Dashboard works perfectly on mobile! 📱

---

## 🛑 STOP THE AGENT:

If you want to stop it:

1. Go to: https://railway.app/dashboard
2. Click your project
3. Click service
4. Click "Stop"

To restart: Click "Deploy"

---

## ❓ STILL STUCK?

Alternative method without Railway:

### Use DigitalOcean ($200 free credit):

1. Sign up: https://www.digitalocean.com/
2. Create Droplet (Ubuntu, $4/month)
3. Use their web console (no CMD needed!)
4. Run these commands:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Upload your files via their web interface
   cd /root/trading-agent
   docker-compose -f docker-compose.cloud.yml up -d
   ```
5. Access: http://YOUR-DROPLET-IP:8080

---

## 🎯 SUMMARY:

```cmd
REM 1. Open CMD in project folder
cd C:\trading-agent

REM 2. Install Railway
npm install -g @railway/cli

REM 3. Login
railway login

REM 4. Initialize
railway init

REM 5. Deploy
railway up

REM 6. Get URL
railway domain

REM 7. Open URL in browser - DONE! 🎉
```

**Your agent runs 24/7 even when your PC is off!** 🚀
