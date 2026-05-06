import requests
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

BASE_URL = "http://uptime.local"
print("=" * 60)
print("UPTIME MONITOR - ДИАГРАММЫ (ТОЛЬКО ОСНОВНЫЕ САЙТЫ)")
print("=" * 60)

# 1. ЛОГИН / LẤY DỮ LIỆU
response = requests.get(f"{BASE_URL}/api/summary")
data = response.json()["summary"]

# ТОЛЬКО 7 ОСНОВНЫХ САЙТОВ / CHỈ 7 WEBSITE CHÍNH
allowed_names = ["Google", "GitHub", "Stack Overflow", "Reddit", "Wikipedia", "Yahoo", "ChatGPT"]
filtered_data = [item for item in data if item["name"] in allowed_names]

names = [row["name"] for row in filtered_data]
up_counts = [row["up_count"] for row in filtered_data]
down_counts = [row["down_count"] for row in filtered_data]
total_checks = [row["total_checks"] for row in filtered_data]
uptime_percents = [row["uptime_percent"] for row in filtered_data]

# 2. ВИЗУАЛИЗАЦИЯ / VẼ BIỂU ĐỒ
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Uptime Monitor - Статистика доступности веб-сайтов', fontsize=14, fontweight='bold')

# ----- КРУГОВАЯ ДИАГРАММА (ПЕРВЫЙ САЙТ) / BIỂU ĐỒ TRÒN (WEBSITE ĐẦU TIÊN) -----
first = filtered_data[0]
up = first["up_count"]
down = first["down_count"]
total = up + down
uptime_pct = (up / total * 100) if total > 0 else 0

axes[0].pie([up, down],
            labels=["Работает", "Не работает"],
            colors=["#4CAF50", "#F44336"],
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"edgecolor": "black"})
axes[0].set_title(f"Доступность: {first['name']}\n(Uptime: {uptime_pct:.1f}%)",
                  fontsize=12, fontweight="bold")

# ----- СТОЛБЧАТАЯ ДИАГРАММА (7 САЙТОВ) / BIỂU ĐỒ CỘT (7 WEBSITE) -----
x = range(len(names))
bars = axes[1].bar(x, total_checks, label="Всего проверок", color="#4CAF50", edgecolor="black")

# Показываем % внутри столбца (белым цветом) / Hiển thị % bên trong cột (màu trắng)
for i, (total, percent) in enumerate(zip(total_checks, uptime_percents)):
    axes[1].text(i, total / 2, f"{percent:.1f}%", ha="center", va="center", fontsize=10, fontweight="bold", color="white")

axes[1].set_xticks(x)
axes[1].set_xticklabels(names, rotation=30, ha="right", fontsize=9)
axes[1].set_ylabel("Количество проверок", fontsize=11)
axes[1].set_title("Статистика доступности по URL (Всего проверок + Uptime %)", fontsize=12, fontweight="bold")
axes[1].legend(fontsize=9)
axes[1].grid(axis="y", linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig("uptime_dashboard.png", dpi=150, bbox_inches="tight")
print("\nДиаграмма сохранена: uptime_dashboard.png")
print("График построен ТОЛЬКО для основных сайтов (БЕЗ тестовых URL).")