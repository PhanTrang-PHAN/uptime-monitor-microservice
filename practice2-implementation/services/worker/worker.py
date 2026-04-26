import asyncio
import aiohttp
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from aiohttp import web
import time

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://uptime_user:uptime_pass@localhost:5432/uptime_db")
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_SECONDS", 30))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

checks_total = Counter('checks_total', 'Total checks performed', ['status'])
check_duration = Histogram('check_duration_seconds', 'Check duration in seconds')

Base = declarative_base()

class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True)
    url = Column(String)
    is_active = Column(Boolean, default=True)

async def check_url(session, url_id, url_address):
    start_time = time.time()
    try:
        async with session.get(url_address, timeout=aiohttp.ClientTimeout(total=10)) as response:
            response_time_ms = (time.time() - start_time) * 1000
            is_available = 200 <= response.status < 400
            check_duration.observe(response_time_ms / 1000)
            if is_available:
                checks_total.labels(status='success').inc()
            else:
                checks_total.labels(status='failed').inc()
            return {
                "url_id": url_id,
                "status_code": response.status,
                "response_time_ms": response_time_ms,
                "is_available": is_available,
                "error_message": None
            }
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        checks_total.labels(status='error').inc()
        return {
            "url_id": url_id,
            "status_code": None,
            "response_time_ms": response_time_ms,
            "is_available": False,
            "error_message": str(e)
        }

async def run_checks():
    while True:
        try:
            db = SessionLocal()
            urls = db.query(URL).filter(URL.is_active == True).all()
            db.close()
            if urls:
                async with aiohttp.ClientSession() as session:
                    tasks = [check_url(session, url.id, url.url) for url in urls]
                    results = await asyncio.gather(*tasks)
                    async with aiohttp.ClientSession() as client:
                        for result in results:
                            try:
                                async with client.post(f"{API_GATEWAY_URL}/api/check-results", json=result) as resp:
                                    if resp.status != 200:
                                        print(f"Failed to send result: {await resp.text()}")
                            except Exception as e:
                                print(f"Error sending result: {e}")
            await asyncio.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"Error in check loop: {e}")
            await asyncio.sleep(CHECK_INTERVAL)

async def health_handler(request):
    return web.json_response({"status": "healthy", "timestamp": str(datetime.utcnow())})

async def metrics_handler(request):
    return web.Response(text=generate_latest(), content_type=CONTENT_TYPE_LATEST)

async def start_worker(app):
    asyncio.create_task(run_checks())

app = web.Application()
app.router.add_get('/health', health_handler)
app.router.add_get('/metrics', metrics_handler)
app.on_startup.append(start_worker)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8001)
