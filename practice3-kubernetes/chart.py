import requests
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Для среды без GUI
import numpy as np

# ============================================
# ПОЛУЧЕНИЕ ДАННЫХ ИЗ API UPTIME MONITOR
# ============================================

print("📡 Загрузка данных из API...")
response = requests.get("http://uptime.local/api/urls")
urls = response.json()

print(f"✅ Найдено {len(urls)} URL-адресов для мониторинга")

# Сбор статистики для каждого URL
names = []
up_counts = []
down_counts = []
total_counts = []

for url in urls:
    url_id = url["id"]
    name = url["name"]
    
    history_resp = requests.get(f"http://uptime.local/api/urls/{url_id}/history")
    history = history_resp.json()
    
    up = sum(1 for h in history if h["is_available"] == True)
    down = sum(1 for h in history if h["is_available"] == False)
    total = len(history)
    
    names.append(name)
    up_counts.append(up)
    down_counts.append(down)
    total_counts.append(total)
    
    print(f"  - {name}: РАБОТАЕТ={up}, НЕ РАБОТАЕТ={down}, Всего={total}")

# ============================================
# ПОСТРОЕНИЕ ДИАГРАММ
# ============================================

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('📊 Uptime Monitor - Статистика доступности веб-сайтов', fontsize=16, fontweight='bold')

# === Диаграмма 1: Круговая диаграмма (общая) ===
total_up = sum(up_counts)
total_down = sum(down_counts)
if total_up + total_down > 0:
    axes[0, 0].pie([total_up, total_down],
                    labels=[f'✅ Работает ({total_up})', f'❌ Не работает ({total_down})'],
                    colors=['#4CAF50', '#F44336'],
                    autopct='%1.1f%%',
                    startangle=90,
                    explode=(0.05, 0))
    axes[0, 0].set_title('Общая статистика', fontsize=12, fontweight='bold')
else:
    axes[0, 0].text(0.5, 0.5, 'Нет данных', ha='center', va='center')
    axes[0, 0].set_title('Общая статистика', fontsize=12)

# === Диаграмма 2: Столбчатая диаграмма (детальная) ===
x = range(len(names))
width = 0.35
axes[0, 1].bar(x, up_counts, width, label='✅ Работает', color='#4CAF50')
axes[0, 1].bar(x, down_counts, width, bottom=up_counts, label='❌ Не работает', color='#F44336')
axes[0, 1].set_xlabel('Веб-сайт')
axes[0, 1].set_ylabel('Количество проверок')
axes[0, 1].set_title('Детальная статистика по сайтам', fontsize=12, fontweight='bold')
axes[0, 1].set_xticks(x)
axes[0, 1].set_xticklabels(names, rotation=45, ha='right', fontsize=9)
axes[0, 1].legend()
axes[0, 1].grid(axis='y', linestyle='--', alpha=0.7)

# === Диаграмма 3: Горизонтальная диаграмма (процент uptime) ===
uptime_percents = []
for i, url in enumerate(names):
    total = up_counts[i] + down_counts[i]
    percent = (up_counts[i] / total * 100) if total > 0 else 0
    uptime_percents.append(percent)

colors = ['#4CAF50' if p >= 95 else '#FFC107' if p >= 80 else '#F44336' for p in uptime_percents]
y_pos = np.arange(len(names))
axes[1, 0].barh(y_pos, uptime_percents, color=colors)
axes[1, 0].set_yticks(y_pos)
axes[1, 0].set_yticklabels(names)
axes[1, 0].set_xlabel('Время безотказной работы (%)')
axes[1, 0].set_title('Процент доступности (Uptime %)', fontsize=12, fontweight='bold')
axes[1, 0].axvline(x=95, color='green', linestyle='--', alpha=0.5, label='Отлично (≥95%)')
axes[1, 0].axvline(x=80, color='orange', linestyle='--', alpha=0.5, label='Средне (≥80%)')
axes[1, 0].legend(fontsize=8)
axes[1, 0].set_xlim(0, 100)

# === Диаграмма 4: График тренда (последние проверки) ===
if urls and len(history) > 0:
    first_url_id = urls[0]["id"]
    history_resp = requests.get(f"http://uptime.local/api/urls/{first_url_id}/history?limit=20")
    recent = history_resp.json()
    
    if recent:
        times = [h["checked_at"][11:16] for h in recent[-10:]]
        statuses = [1 if h["is_available"] else 0 for h in recent[-10:]]
        
        axes[1, 1].plot(times, statuses, marker='o', linestyle='-', color='#2196F3', linewidth=2)
        axes[1, 1].fill_between(times, statuses, alpha=0.3, color='#2196F3')
        axes[1, 1].set_ylim(-0.1, 1.1)
        axes[1, 1].set_yticks([0, 1])
        axes[1, 1].set_yticklabels(['❌ Не работает', '✅ Работает'])
        axes[1, 1].set_xlabel('Время')
        axes[1, 1].set_title(f'Тренд доступности: {names[0]}', fontsize=12, fontweight='bold')
        axes[1, 1].grid(axis='x', linestyle='--', alpha=0.5)
        plt.setp(axes[1, 1].xaxis.get_majorticklabels(), rotation=45, ha='right')
else:
    axes[1, 1].text(0.5, 0.5, 'Нет данных для отображения тренда', ha='center', va='center')
    axes[1, 1].set_title('Тренд доступности', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('practice3-kubernetes/uptime_dashboard.png', dpi=150, bbox_inches='tight')
print("\n✅ Диаграмма сохранена: practice3-kubernetes/uptime_dashboard.png")
print("📊 Файл диаграммы готов для отчета!")
