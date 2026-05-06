from fastapi import FastAPI, Query
from fastapi.responses import Response
import csv
import requests
from io import StringIO
from datetime import datetime

app = FastAPI()

BASE_URL = "http://localhost:8000"

@app.get("/")
def root():
    return {"message": "Report Service", "endpoints": ["/report", "/export", "/history_csv"]}

@app.get("/report")
def get_report():
    try:
        resp = requests.get(f"{BASE_URL}/api/urls")
        if resp.status_code != 200:
            return {"error": "API Gateway not reachable"}
        urls = resp.json()
        total_urls = len(urls)
        total_checks = 0
        for url in urls:
            hist_resp = requests.get(f"{BASE_URL}/api/urls/{url['id']}/history")
            if hist_resp.status_code == 200:
                total_checks += len(hist_resp.json())
        return {
            "report": {
                "generated_at": datetime.now().isoformat(),
                "total_urls_monitored": total_urls,
                "total_checks_performed": total_checks,
                "system_status": "healthy"
            }
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/export")
def export_csv():
    """Tải file CSV tổng hợp các URL đang theo dõi"""
    try:
        resp = requests.get(f"{BASE_URL}/api/urls")
        if resp.status_code != 200:
            return {"error": "API Gateway not reachable"}
        
        urls = resp.json()
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["URL ID", "Name", "URL", "Status", "Last Check"])
        
        for url in urls:
            writer.writerow([
                url["id"],
                url["name"],
                url["url"],
                "active" if url["is_active"] else "inactive",
                url.get("last_check_at", "N/A")
            ])
        
        # Trả về CSV dưới dạng Response
        csv_content = output.getvalue()
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=uptime_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    except Exception as e:
        return {"error": str(e)}

@app.get("/history_csv")
def history_csv(url: str = Query(...)):
    """Tải file CSV lịch sử kiểm tra của một URL cụ thể"""
    try:
        resp = requests.get(f"{BASE_URL}/api/urls")
        if resp.status_code != 200:
            return {"error": "API Gateway not reachable"}
        
        urls = resp.json()
        target = next((u for u in urls if u["url"] == url), None)
        if not target:
            return {"error": f"URL not found: {url}"}
        
        hist_resp = requests.get(f"{BASE_URL}/api/urls/{target['id']}/history")
        history = hist_resp.json()
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Checked At", "Status Code", "Response Time (ms)", "Available", "Error"])
        
        for h in history:
            writer.writerow([
                h["checked_at"],
                h["status_code"],
                h["response_time_ms"],
                "Yes" if h["is_available"] else "No",
                h["error_message"] or ""
            ])
        
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]
        csv_content = output.getvalue()
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=history_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    except Exception as e:
        return {"error": str(e)}