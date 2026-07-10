"""
Keep Render.com free tier service awake
Use with cron job service like cron-job.org or uptimerobot.com

Setup:
1. Deploy app to Render
2. Go to cron-job.org
3. Create new cron job:
   - URL: https://your-app.onrender.com/healthz
   - Interval: Every 14 minutes
   - This prevents the free tier from sleeping
"""
import requests
import time
from datetime import datetime

# Your Render.com app URL
APP_URL = "https://your-app-name.onrender.com/healthz"

def ping_service():
    """Ping the service to keep it awake"""
    try:
        response = requests.get(APP_URL, timeout=30)
        status = "✅ OK" if response.status_code == 200 else f"⚠️ {response.status_code}"
        print(f"[{datetime.now()}] {status} - {APP_URL}")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print(f"🔄 Starting keep-alive service for {APP_URL}")
    print("Press Ctrl+C to stop\n")
    
    while True:
        ping_service()
        # Wait 14 minutes (Render free tier sleeps after 15 min)
        time.sleep(14 * 60)
