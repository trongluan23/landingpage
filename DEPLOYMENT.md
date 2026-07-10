# 🚀 Deployment Guide - Render.com

## 📋 Prerequisites

1. GitHub account
2. Render.com account (free): https://render.com
3. OpenAI API key

## 🎯 Quick Deploy (5 minutes)

### Method 1: One-Click Deploy với Blueprint

1. **Push code lên GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/pageforge.git
git push -u origin main
```

2. **Deploy trên Render**
   - Đi tới: https://render.com/deploy
   - Paste repo URL: `https://github.com/yourusername/pageforge`
   - Render sẽ tự động detect `render.yaml`
   - Click "Apply"

3. **Configure Environment Variables**
   - Trong Render dashboard, vào service settings
   - Add environment variable:
     ```
     OPENAI_API_KEY = sk-proj-your-key-here
     ```

4. **Done!** 🎉
   - Service sẽ tự động deploy
   - PostgreSQL database tự động tạo và connect
   - URL: `https://pageforge.onrender.com`

### Method 2: Manual Deploy

#### Step 1: Create PostgreSQL Database

1. Login to Render.com
2. Click "New +" → "PostgreSQL"
3. Name: `pageforge-db`
4. Database Name: `landing_pages`
5. Region: `Oregon (US West)`
6. Plan: **Free**
7. Click "Create Database"
8. **Save the Internal Database URL** (bắt đầu với `postgresql://`)

#### Step 2: Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   ```
   Name: pageforge
   Region: Oregon (US West)
   Branch: main
   Root Directory: (leave blank)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   Plan: Free
   ```

#### Step 3: Add Environment Variables

Click "Advanced" → "Add Environment Variable":

```env
OPENAI_API_KEY = sk-proj-your-openai-key
OPENAI_MODEL = gpt-4o-mini
DATABASE_URL = [paste Internal Database URL from Step 1]
SECRET_KEY = [generate random string]
PYTHON_VERSION = 3.11.0
```

#### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for build (~2-3 minutes)
3. Database tables sẽ tự động tạo khi app start
4. Access your app: `https://your-service-name.onrender.com`

## 🔧 Post-Deploy Configuration

### Custom Domain (Optional)

1. Go to service Settings → Custom Domain
2. Add your domain: `pageforge.yourdomain.com`
3. Update DNS:
   ```
   CNAME pageforge → your-service.onrender.com
   ```

### Auto-Deploy from GitHub

Render tự động deploy mỗi khi push code mới lên GitHub!

```bash
git add .
git commit -m "New feature"
git push
```

## 📊 Monitoring

### View Logs
```
Dashboard → Service → Logs
```

### Database Access
```bash
# Get connection string from Render dashboard
psql [External Database URL]
```

### Service Status
```
https://pageforge.onrender.com/healthz
```

## ⚠️ Free Tier Limitations

**Render.com Free Plan:**
- ✅ 750 hours/month (enough for 1 service)
- ✅ PostgreSQL 1GB storage
- ✅ Auto-deploy from GitHub
- ⚠️ Sleeps after 15 min inactive (cold start ~30s)
- ⚠️ Limited bandwidth

**Tips for Free Tier:**
- App sleeps after inactivity → first request takes ~30s
- Use cron job to ping every 14 min: https://cron-job.org
- Database limited to 1GB → monitor usage

## 🔄 Alternative: Heroku Deploy

```bash
# Install Heroku CLI
heroku login
heroku create pageforge

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set OPENAI_API_KEY=sk-proj-your-key
heroku config:set OPENAI_MODEL=gpt-4o-mini

# Deploy
git push heroku main

# Open app
heroku open
```

## 🐳 Alternative: Docker Deploy

### Build Image
```bash
docker build -t pageforge .
docker run -p 5000:5000 \
  -e OPENAI_API_KEY=your-key \
  -e DATABASE_URL=postgresql://... \
  pageforge
```

### Docker Compose
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/landing_pages
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: landing_pages
      POSTGRES_PASSWORD: postgres
```

## 🐛 Troubleshooting

### Build Fails
- Check Python version in `runtime.txt`
- Verify all dependencies in `requirements.txt`
- Check logs: `Dashboard → Logs`

### Database Connection Error
- Verify DATABASE_URL is correct
- Use **Internal Database URL** (not External)
- Check database is running

### App Not Responding
- Free tier: cold start takes ~30s
- Check service status in dashboard
- View logs for errors

### OpenAI API Error
- Verify OPENAI_API_KEY is set
- Check API key is valid: https://platform.openai.com/api-keys
- Ensure you have credits

## 📝 Environment Variables Reference

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | `sk-proj-xxx` | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Model to use |
| `DATABASE_URL` | ✅ Yes | `postgresql://...` | PostgreSQL connection |
| `SECRET_KEY` | No | `random-string` | Flask secret key |
| `PORT` | No | `5000` | Port (auto-set by Render) |

## 🎉 Success Checklist

- ✅ App builds successfully
- ✅ Database connected
- ✅ Homepage loads: `/`
- ✅ Health check works: `/healthz`
- ✅ Can generate landing page
- ✅ Gallery page works: `/gallery`
- ✅ Pages saved to database

## 🔗 Useful Links

- Render Dashboard: https://dashboard.render.com
- Render Docs: https://render.com/docs
- PostgreSQL Docs: https://render.com/docs/databases
- Support: https://render.com/support

---

Need help? Check logs first:
```
Dashboard → Your Service → Logs
```
