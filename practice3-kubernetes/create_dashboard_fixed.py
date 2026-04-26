import requests
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import random
import platform

# ============================================
# CẤU HÌNH FONT HỖ TRỢ TIẾNG NGA
# ============================================
# Tìm font có hỗ trợ Cyrillic
import matplotlib.font_manager as fm

# Thử các font phổ biến trên Windows
font_names = ['Arial', 'DejaVu Sans', 'Times New Roman', 'Segoe UI', 'Tahoma']
selected_font = None
for font in font_names:
    if any(f.name == font for f in fm.fontManager.ttflist):
        selected_font = font
        break

if selected_font:
    plt.rcParams['font.family'] = selected_font
    print(f"✅ Đã chọn font: {selected_font}")
else:
    # Dùng font mặc định
    print("⚠️ Không tìm thấy font Cyrillic, dùng mặc định")

# ============================================
# LẤY DỮ LIỆU
# ============================================
BASE_URL = "http://uptime.local"
print("=" * 60)
print("📊 UPTIME MONITOR - VẼ BIỂU ĐỒ TIẾNG NGA")
print("=" * 60)

print("\n📡 Lấy dữ liệu từ API /summary...")
response = requests.get(f"{BASE_URL}/api/summary")
data = response.json()["summary"]

names = [row["name"] for row in data]
up_counts = [row["up_count"] for row in data]
down_counts = [row["down_count"] for row in data]
uptime_percents = [row["uptime_percent"] for row in data]

print(f"\n📊 Tìm thấy {len(names)} URLs:")
for i, name in enumerate(names):
    print(f"   {name}: Uptime={uptime_percents[i]:.1f}%")

# ============================================
# VẼ BIỂU ĐỒ
# ============================================
print("\n🎨 Đang vẽ biểu đồ...")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('📊 Uptime Monitor - Статистика доступности веб-сайтов', fontsize=14, fontweight='bold')

# --- Biểu đồ 1: Pie chart cho URL đầu tiên ---
if data:
    first = data[0]
    up = first["up_count"]
    down = first["down_count"]
    total = up + down
    uptime_pct = (up / total * 100) if total > 0 else 0
    
    # Sử dụng tiếng Nga trực tiếp
    labels = ['Работает', 'Не работает']
    colors = ['#4CAF50', '#F44336']
    
    axes[0].pie([up, down],
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                wedgeprops={'edgecolor': 'black'})
    axes[0].set_title(f'Доступность: {first["name"]}\n(Uptime: {uptime_pct:.1f}%)', 
                      fontsize=12, fontweight='bold')

# --- Biểu đồ 2: Bar chart cho tất cả URLs ---
x = range(len(names))
bars_up = axes[1].bar(x, uptime_percents, label='Работает %', color='#4CAF50', edgecolor='black')

# Thêm giá trị phần trăm trên cột
for i, percent in enumerate(uptime_percents):
    axes[1].text(i, percent + 1, f'{percent:.1f}%', ha='center', fontsize=9, fontweight='bold')

axes[1].set_xticks(x)
axes[1].set_xticklabels(names, rotation=30, ha='right', fontsize=9)
axes[1].set_ylabel('Процент доступности (%)', fontsize=11)
axes[1].set_title('Статистика доступности по URL', fontsize=12, fontweight='bold')
axes[1].set_ylim(0, 105)
axes[1].grid(axis='y', linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig('practice3-kubernetes/uptime_dashboard_fixed.png', dpi=150, bbox_inches='tight')
print("\n✅ Biểu đồ đã được lưu: practice3-kubernetes/uptime_dashboard_fixed.png")

print("\n" + "=" * 60)
print("📈 TỔNG KẾT:")
print(f"   - Tổng số URLs: {len(names)}")
print(f"   - Trung bình uptime: {sum(uptime_percents)/len(uptime_percents):.1f}%")
print(f"   - Cao nhất: {max(uptime_percents):.1f}%")
print(f"   - Thấp nhất: {min(uptime_percents):.1f}%")
print("=" * 60)
