import requests
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import random
import numpy as np
from datetime import datetime, timedelta

BASE_URL = "http://uptime.local"
print("=" * 60)
print("📊 UPTIME MONITOR - TẠO DỮ LIỆU VÀ VẼ BIỂU ĐỒ")
print("=" * 60)

# ============================================
# 1. TẠO DỮ LIỆU TEST
# ============================================
print("\n📡 1. Lấy danh sách URLs...")
response = requests.get(f"{BASE_URL}/api/urls")
urls = response.json()
print(f"   ✅ Tìm thấy {len(urls)} URLs")

# Danh sách URLs để tạo dữ liệu
urls_to_monitor = [
    {"id": 1, "name": "Google", "url": "https://google.com"},
    {"id": 2, "name": "GitHub", "url": "https://github.com"},
    {"id": 3, "name": "Stack Overflow", "url": "https://stackoverflow.com"},
    {"id": 4, "name": "Reddit", "url": "https://reddit.com"},
    {"id": 5, "name": "Wikipedia", "url": "https://wikipedia.org"},
    {"id": 6, "name": "Yahoo", "url": "https://yahoo.com"},
    {"id": 7, "name": "ChatGPT", "url": "https://chat.openai.com"},
]

print("\n📝 2. Tạo dữ liệu kiểm tra giả lập...")

for url in urls_to_monitor[:7]:
    records = []
    total_checks = random.randint(80, 150)
    up_count = 0
    
    for i in range(total_checks):
        # Tạo dữ liệu ngẫu nhiên: 85% thành công, 15% thất bại
        is_available = random.random() > 0.15
        if is_available:
            up_count += 1
            status_code = 200
            error_msg = None
        else:
            status_code = random.choice([500, 404, 503, 504])
            error_msg = "Connection timeout" if status_code == 504 else "Server error"
        
        response_time = random.uniform(50, 800) if is_available else random.uniform(100, 2000)
        
        records.append({
            "url_id": url["id"],
            "status_code": status_code,
            "response_time_ms": response_time,
            "is_available": is_available,
            "error_message": error_msg
        })
    
    # Gửi bulk insert
    resp = requests.post(f"{BASE_URL}/api/history/bulk", json={"records": records})
    uptime_pct = (up_count / total_checks) * 100
    print(f"   📊 {url['name']}: {total_checks} checks, UP={up_count}, DOWN={total_checks-up_count}, Uptime={uptime_pct:.1f}%")
    print(f"      ✅ Inserted {total_checks} records")

print("\n✅ Dữ liệu đã được tạo thành công!")

# ============================================
# 2. LẤY DỮ LIỆU THỰC TẾ
# ============================================
print("\n📡 3. Lấy dữ liệu thống kê từ API...")
response = requests.get(f"{BASE_URL}/api/summary")
data = response.json()["summary"]

names = [row["name"] for row in data]
up_counts = [row["up_count"] for row in data]
down_counts = [row["down_count"] for row in data]
total_checks = [row["total_checks"] for row in data]
uptime_percents = [row["uptime_percent"] for row in data]

print("\n📊 Kết quả thống kê:")
print("-" * 60)
print(f"{'Website':<15} {'UP':<8} {'DOWN':<8} {'Total':<8} {'Uptime':<8}")
print("-" * 60)
for i, name in enumerate(names):
    print(f"{name:<15} {up_counts[i]:<8} {down_counts[i]:<8} {total_checks[i]:<8} {uptime_percents[i]:.1f}%")
print("-" * 60)

# ============================================
# 3. VẼ BIỂU ĐỒ (NHƯ MẪU BẠN YÊU CẦU)
# ============================================
print("\n 4. Đang vẽ biểu đồ...")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle(' Uptime Monitor - Статистика доступности веб-сайтов', fontsize=14, fontweight='bold')

# --- Biểu đồ 1: Pie chart cho URL đầu tiên ---
if data:
    first = data[0]
    up = first["up_count"]
    down = first["down_count"]
    total = up + down
    uptime_pct = (up / total * 100) if total > 0 else 0
    
    axes[0].pie([up, down],
                labels=[" Работает", " Не работает"],
                colors=["#4CAF50", "#F44336"],
                autopct="%1.1f%%",
                startangle=90,
                wedgeprops={"edgecolor": "black"})
    axes[0].set_title(f"Доступность: {first['name']}\n(Uptime: {uptime_pct:.1f}%)", 
                      fontsize=12, fontweight="bold")

# --- Biểu đồ 2: Bar chart cho tất cả URLs ---
x = range(len(names))
bars_up = axes[1].bar(x, up_counts, label=" Работает", color="#4CAF50", edgecolor="black")
bars_down = axes[1].bar(x, down_counts, bottom=up_counts, label=" Не работает", color="#F44336", edgecolor="black")

# Thêm nhãn phần trăm uptime trên cột
for i, (up, down) in enumerate(zip(up_counts, down_counts)):
    total = up + down
    if total > 0:
        percent = up / total * 100
        axes[1].text(i, up + down + 1, f"{percent:.1f}%", ha="center", fontsize=9, fontweight="bold")

axes[1].set_xticks(x)
axes[1].set_xticklabels(names, rotation=30, ha="right", fontsize=9)
axes[1].set_ylabel("Количество проверок", fontsize=11)
axes[1].set_title("Статистика доступности по URL", fontsize=12, fontweight="bold")
axes[1].legend(fontsize=9)
axes[1].grid(axis="y", linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig("practice3-kubernetes/uptime_dashboard.png", dpi=150, bbox_inches="tight")
print("\n Biểu đồ đã được lưu: practice3-kubernetes/uptime_dashboard.png")
print(" File: uptime_dashboard.png")

# ============================================
# 4. HIỂN THỊ THÔNG TIN
# ============================================
print("\n" + "=" * 60)
print(" TỔNG KẾT:")
print(f"   - Tổng số URLs: {len(names)}")
print(f"   - Tổng số lần kiểm tra: {sum(total_checks)}")
print(f"   - Tổng số lần thành công: {sum(up_counts)}")
print(f"   - Tổng số lần thất bại: {sum(down_counts)}")
print(f"   - Tỷ lệ thành công chung: {sum(up_counts)/sum(total_checks)*100:.1f}%" if sum(total_checks) > 0 else "   - Chưa có dữ liệu")
print("=" * 60)
