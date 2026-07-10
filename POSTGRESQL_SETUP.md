# PostgreSQL Setup Guide

## 🐘 Option 1: Quick Setup (Automatic)

```bash
python setup_postgres.py
```

Nhập thông tin:
- Host: `localhost`
- Port: `5432`
- User: `postgres`
- Password: mật khẩu PostgreSQL của bạn
- Database: `landing_pages`

Script sẽ tự động:
✅ Tạo database
✅ Tạo tables
✅ Cập nhật `.env`

## 🔧 Option 2: Manual Setup

### 1. Cài đặt PostgreSQL

**Windows:**
- Download: https://www.postgresql.org/download/windows/
- Chạy installer, nhớ mật khẩu cho user `postgres`

**Mac:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux:**
```bash
sudo apt-get install postgresql
sudo service postgresql start
```

### 2. Tạo Database

```bash
# Đăng nhập PostgreSQL
psql -U postgres

# Tạo database
CREATE DATABASE landing_pages;

# Tạo user (optional)
CREATE USER pageforge WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE landing_pages TO pageforge;

# Thoát
\q
```

### 3. Cập nhật .env

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/landing_pages
```

### 4. Tạo Tables

```bash
python -c "from models import init_db; init_db()"
```

## ☁️ Option 3: Cloud PostgreSQL (Free)

### Render.com
1. Tạo account: https://render.com
2. New → PostgreSQL
3. Copy "External Database URL"
4. Paste vào `.env`:
```env
DATABASE_URL=postgresql://user:pass@dpg-xxx.oregon-postgres.render.com/dbname
```

### Neon.tech
1. Tạo account: https://neon.tech
2. Create project
3. Copy connection string
4. Paste vào `.env`

### Supabase
1. Tạo account: https://supabase.com
2. New project
3. Settings → Database → Connection string
4. Paste vào `.env`

## 🧪 Test Connection

```bash
python -c "from models import get_session; print('✅ Connected!' if get_session() else '❌ Failed')"
```

## 🔄 Switch back to SQLite

Trong `.env`:
```env
DATABASE_URL=sqlite:///landing_pages.db
```

No PostgreSQL needed!

## 🐛 Troubleshooting

### "psycopg2 not installed"
```bash
pip install psycopg2-binary
```

### "could not connect to server"
- Kiểm tra PostgreSQL đang chạy
- Check firewall/port 5432
- Verify username/password

### "database does not exist"
```bash
python setup_postgres.py
```
hoặc tạo manual với `CREATE DATABASE landing_pages;`

### Windows specific: "libpq.dll not found"
- Reinstall PostgreSQL
- Hoặc dùng SQLite: `DATABASE_URL=sqlite:///landing_pages.db`
