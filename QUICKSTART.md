# 🚀 Quick Start Guide

## 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 2️⃣ Configure Database

Edit `.env` file:

### Option A: PostgreSQL (Recommended)

**Local PostgreSQL:**
```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/landing_pages
```

**Cloud PostgreSQL (Render/Neon/Supabase):**
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Option B: SQLite (No setup)

```env
DATABASE_URL=sqlite:///landing_pages.db
```

## 3️⃣ Add OpenAI API Key

In `.env`:
```env
OPENAI_API_KEY=sk-proj-your-key-here
```

## 4️⃣ Run App

```bash
python app.py
```

That's it! 🎉

## What Happens Automatically:

✅ App connects to database
✅ Creates tables if they don't exist
✅ Starts server at http://localhost:5000

## No Need For:

❌ Running `setup_postgres.py`
❌ Manually creating tables
❌ Separate database initialization

## Logs You'll See:

```
INFO:landing-generator:Connecting to database...
🔌 Connecting to: postgresql://postgres:****@localhost:5432/landing_pages
✅ Database connection successful
📋 Creating tables if not exist...
✅ Tables ready
✅ Database connected and initialized successfully
✅ Database connection test passed
 * Running on http://127.0.0.1:5000
```

## If Database Connection Fails:

App will:
1. Log the error
2. Try to fallback to SQLite
3. Continue running (database features may not work)

Check logs for errors and verify:
- PostgreSQL is running
- DATABASE_URL is correct
- Database exists
- Credentials are valid

## Testing Connection:

```bash
# Test database connection
python -c "from models import init_db; init_db(); print('✅ Success!')"
```

## Deploy to Render:

```bash
git push origin main
```

Render will:
- Auto-detect Python
- Install dependencies
- Connect to PostgreSQL
- Create tables automatically
- Start app

No manual setup needed! 🚀
