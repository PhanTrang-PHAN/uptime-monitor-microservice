from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import os
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://uptime_user:uptime_pass@localhost:5432/uptime_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    check_interval_seconds = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    last_check_at = Column(DateTime, nullable=True)

class CheckHistory(Base):
    __tablename__ = "check_history"
    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, nullable=False)
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    is_available = Column(Boolean, default=False)
    error_message = Column(String, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow())

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic schemas
class URLCreate(BaseModel):
    name: str
    url: str
    check_interval_seconds: Optional[int] = 60

class URLResponse(BaseModel):
    id: int
    name: str
    url: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class CheckHistoryResponse(BaseModel):
    id: int
    url_id: int
    status_code: Optional[int]
    response_time_ms: Optional[float]
    is_available: bool
    error_message: Optional[str]
    checked_at: datetime

# Prometheus metrics
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
urls_created_total = Counter('urls_created_total', 'Total URLs created')

# FastAPI app
app = FastAPI(title="Uptime Monitor API", version="1.0.0")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Uptime Monitor API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/urls", response_model=URLResponse)
def create_url(url_data: URLCreate, db: Session = Depends(get_db)):
    urls_created_total.inc()
    existing = db.query(URL).filter(URL.url == url_data.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="URL already exists")
    new_url = URL(name=url_data.name, url=url_data.url, check_interval_seconds=url_data.check_interval_seconds)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return new_url

@app.get("/api/urls", response_model=List[URLResponse])
def get_urls(db: Session = Depends(get_db)):
    return db.query(URL).filter(URL.is_active == True).all()

@app.delete("/api/urls/{url_id}")
def delete_url(url_id: int, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.id == url_id).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    url.is_active = False
    db.commit()
    return {"message": "URL deleted"}

@app.get("/api/urls/{url_id}/history", response_model=List[CheckHistoryResponse])
def get_history(url_id: int, limit: int = 50, db: Session = Depends(get_db)):
    history = db.query(CheckHistory).filter(CheckHistory.url_id == url_id).order_by(desc(CheckHistory.checked_at)).limit(limit).all()
    return history

@app.post("/api/check-results")
def receive_check_result(data: dict, db: Session = Depends(get_db)):
    history = CheckHistory(
        url_id=data.get("url_id"),
        status_code=data.get("status_code"),
        response_time_ms=data.get("response_time_ms"),
        is_available=data.get("is_available", False),
        error_message=data.get("error_message")
    )
    db.add(history)
    url = db.query(URL).filter(URL.id == data.get("url_id")).first()
    if url:
        url.last_check_at = datetime.utcnow()
    db.commit()
    return {"message": "Result received"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
