# 🔧 Render.com psycopg2 Error Fix

## ❌ Error:
```
undefined symbol: _PyInterpreterState_Get
```

## ✅ Solutions (Try in order):

### Solution 1: Redeploy với updated files

Files đã được update:
- `runtime.txt` → Python 3.11.9
- `requirements.txt` → psycopg2-binary 2.9.10
- `models.py` → Added postgres:// → postgresql:// fix

**Steps:**
```bash
git add .
git commit -m "Fix psycopg2 compatibility"
git push origin main
```

Render sẽ auto-redeploy.

### Solution 2: Manual Environment Variable (Nếu Solution 1 không work)

1. Go to Render Dashboard
2. Your Service → Environment
3. Add:
   ```
   PYTHON_VERSION = 3.11.9
   ```
4. Manual Deploy → Clear build cache & deploy

### Solution 3: Use psycopg2 instead of psycopg2-binary

Trong Render Dashboard:

1. Environment → Build Command
2. Change to:
   ```bash
   pip install psycopg2==2.9.10 && pip install -r requirements.txt --no-deps
   ```

### Solution 4: Completely rebuild

1. Delete current service
2. Create new Web Service
3. Use updated code từ GitHub
4. Set environment variables:
   ```
   OPENAI_API_KEY = your-key
   DATABASE_URL = [from PostgreSQL service]
   PYTHON_VERSION = 3.11.9
   ```

## 🧪 Verify Fix

After deploy, check:

1. **Logs**
   ```
   Dashboard → Service → Logs
   ```
   Should see: "Database initialized successfully"

2. **Health Check**
   ```
   https://your-app.onrender.com/healthz
   ```
   Should return: `{"status": "ok"}`

3. **Test Generate**
   - Go to homepage
   - Try generating a landing page
   - Check gallery page

## 🐛 Still Having Issues?

### Check Python Version in Logs:
```
Look for: "Python 3.11.9" in build logs
```

### Check psycopg2 Version:
```
Look for: "psycopg2-binary==2.9.10" or "psycopg2==2.9.10"
```

### Force Clean Build:
1. Dashboard → Manual Deploy
2. Check "Clear build cache"
3. Deploy

### Use SQLite as temporary workaround:
In Render Environment Variables:
```
DATABASE_URL = sqlite:///landing_pages.db
```
(Not recommended for production, but works for testing)

## 📝 What Changed:

| File | Change | Why |
|------|--------|-----|
| `runtime.txt` | Python 3.11.9 | Better compatibility |
| `requirements.txt` | psycopg2-binary 2.9.10 | Fixed binary version |
| `models.py` | postgres:// → postgresql:// | Render uses new format |
| `models.py` | pool_pre_ping=True | Better connection handling |

## 🎯 Expected Result:

After fix:
- ✅ Service builds successfully
- ✅ Database connects
- ✅ Can generate landing pages
- ✅ Gallery works
- ✅ No psycopg2 errors in logs
