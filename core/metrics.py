
"""
import matplotlib.pyplot as plt
import os
import pandas as pd

# Переход в корень проекта
os.chdir(os.path.dirname(os.path.dirname(__file__)))


# Пути к папкам
RESULTS_DIR = "results"
TRADES_DIR = os.path.join(RESULTS_DIR, "trades")
TRADE_PLOTS_DIR = os.path.join(RESULTS_DIR, "trade_plots")

# Создаём папку для графиков трейдов
os.makedirs(TRADE_PLOTS_DIR, exist_ok=True)

# Загружаем исторические данные
historical_data = pd.read_parquet("data/historical_data.parquet")
historical_data.columns = historical_data.columns.str.lower()
historical_data['open_time'] = pd.to_datetime(historical_data['open_time'], unit='ms')
historical_data = historical_data.set_index(['open_time', 'symbol']).sort_index()

# Функция для построения графика

def plot_trades_for_symbol(symbol, trades_df, price_df, strategy_name):
    if price_df.empty or trades_df.empty:
        print(f"⚠️ Нет данных для {symbol} в {strategy_name.upper()}.")
        return

    plt.figure(figsize=(14, 8))
    plt.plot(price_df.index, price_df.values, label='Close Price', color='blue')

    # Отметим входы и выходы
    entries = trades_df['Entry Timestamp']
    exits = trades_df['Exit Timestamp']
    entry_prices = trades_df['Avg Entry Price']
    exit_prices = trades_df['Avg Exit Price']

    plt.scatter(entries, entry_prices, color='green', label='Entry', marker='^', s=100)
    plt.scatter(exits, exit_prices, color='red', label='Exit', marker='v', s=100)

    plt.title(f"Трейды по {symbol} ({strategy_name.upper()})")
    plt.xlabel("Дата")
    plt.ylabel("Цена")
    plt.legend()
    plt.grid(True)

    save_path = os.path.join(TRADE_PLOTS_DIR, f"{strategy_name}_{symbol}_trades.png")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"✅ График трейдов сохранён: {save_path}")

# Стратегии для обработки
strategies = ["sma", "rsi", "vwap"]

for strategy in strategies:
    trades_path = os.path.join(TRADES_DIR, f"{strategy}_trades.csv")
    if not os.path.exists(trades_path):
        print(f"❌ Файл трейдов не найден для {strategy.upper()}: {trades_path}")
        continue

    trades_df = pd.read_csv(trades_path)

    if trades_df.empty:
        print(f"⚠️ Нет трейдов для {strategy.upper()}.")
        continue

    # Выбираем топ-5 символов по прибыли
    top_symbols = trades_df.groupby('Column')['Return'].sum().sort_values(ascending=False).head(5).index

    for symbol in top_symbols:
        # Фильтруем трейды для этой пары
        symbol_trades = trades_df[trades_df['Column'] == symbol]

        # Берем цены для пары
        try:
            close_prices = historical_data.xs(symbol, level='symbol')['close']
        except KeyError:
            print(f"⚠️ Нет данных по цене для {symbol}")
            continue

        # Рисуем график
        plot_trades_for_symbol(symbol, symbol_trades, close_prices, strategy)

print("\n🏁 Все графики трейдов построены!")
"""


import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import webbrowser

# === Пути ===
RESULTS_DIR = "results"
TRADES_DIR = os.path.join(RESULTS_DIR, "trades")
REPORT_PATH = os.path.join(RESULTS_DIR, "report.html")

# Установим рабочую директорию в корень проекта
os.chdir(os.path.dirname(os.path.dirname(__file__)))

os.makedirs(RESULTS_DIR, exist_ok=True)

# === Стратегии ===
strategies = ["sma", "rsi", "vwap"]

# === Загружаем метрики ===
metrics_list = []

for strat in strategies:
    stats_path = os.path.join(RESULTS_DIR, f"{strat}_stats.csv")
    if not os.path.exists(stats_path):
        print(f"⚠️ Нет файла статистики для {strat.upper()}.")
        continue

    stats = pd.read_csv(stats_path, index_col=0).T
    stats["Strategy"] = strat

    # Преобразуем строки в числа, если это возможно
    for col in stats.columns:
        if col != "Strategy":
            stats[col] = pd.to_numeric(stats[col], errors="coerce")

    metrics_list.append(stats)

# Проверяем наличие загруженных метрик
if not metrics_list:
    print("❌ Нет метрик для отчета.")
    exit()

metrics = pd.concat(metrics_list)

# === HTML блоки ===
html_parts = []

# Базовая HTML структура
html_parts.append("""
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>📈 Отчет по стратегиям</title>
<style>
body { font-family: Arial, sans-serif; margin: 20px; }
h1, h2 { color: #2c3e50; }
table { border-collapse: collapse; width: 100%; margin-bottom: 40px; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
th { background-color: #4CAF50; color: white; }
tr:nth-child(even) { background-color: #f2f2f2; }
.metric-best { background-color: #c8e6c9; font-weight: bold; }
.download-btn {
    display: inline-block;
    padding: 10px 20px;
    background-color: #4CAF50;
    color: white;
    font-size: 18px;
    text-decoration: none;
    border-radius: 5px;
    margin-bottom: 30px;
}
</style>
</head>
<body>
""")

html_parts.append('<h1>📊 Аналитика стратегий</h1>')
html_parts.append(f'<a href="{os.path.basename(REPORT_PATH)}" download class="download-btn">📥 Скачать отчет</a>')

# === 1. Equity Curve ===
html_parts.append("<h2>1. Equity Curve по стратегиям</h2>")

initial_balance = 10000  # начальный баланс

for strat in strategies:
    trades_path = os.path.join(TRADES_DIR, f"{strat}_trades.csv")
    if not os.path.exists(trades_path):
        continue

    trades = pd.read_csv(trades_path)
    if trades.empty or "Return" not in trades.columns:
        continue

    # Ограничиваем экстремальные возвраты
    trades["Return"] = trades["Return"].apply(
        lambda x: min(x, 100) if x > 0 else x)

    # Убираем дубликаты по времени выхода
    trades = trades.drop_duplicates(subset="Exit Timestamp", keep="last")

    # Вычисляем накопленную доходность
    trades["Cumulative Return"] = (1 + trades["Return"]).cumprod().fillna(1)
    trades["Cumulative Balance"] = initial_balance * trades["Cumulative Return"]

    # Защита от нулевого начального баланса
    if trades["Cumulative Balance"].iloc[0] == 0:
        trades["Cumulative Balance"] = initial_balance * (1 + trades["Return"]).cumprod()

    # Строим график через Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(trades["Exit Timestamp"]),
        y=trades["Cumulative Balance"],
        mode="lines",
        name=f"{strat.upper()} Strategy"
    ))
    fig.update_layout(
        title=f"Equity Curve ({strat.upper()})",
        xaxis_title="Дата",
        yaxis_title="Баланс портфеля",
        height=400
    )

    html_parts.append(fig.to_html(full_html=False, include_plotlyjs=True))

# === 2. Heatmap по Total Return ===
html_parts.append("<h2>2. Heatmap по Total Return [%]</h2>")

print("Названия столбцов в metrics:")
print(metrics.columns.tolist())

pivot = metrics.pivot_table(values="Total Return [%]", index="Strategy")

plt.figure(figsize=(8, 3))
sns.heatmap(pivot, annot=True, cmap="coolwarm", fmt=".2f")
heatmap_path = os.path.join(RESULTS_DIR, "heatmap.png")
plt.title("Total Return [%] по стратегиям")
plt.tight_layout()
plt.savefig(heatmap_path)
plt.close()

html_parts.append(f'<img src="heatmap.png" style="width:600px;">')

# === 3. Сравнение метрик ===
html_parts.append("<h2>3. Сравнение метрик по стратегиям</h2>")

avg_metrics = metrics.groupby("Strategy").mean()

# Конвертируем в object для вставки HTML-тегов
styled_table = avg_metrics.round(2).astype("object").copy()

# Подсветка лучших метрик
for col in ["Total Return [%]", "Win Rate [%]", "Profit Factor"]:
    best_strategy = avg_metrics[col].idxmax()
    styled_table.loc[best_strategy, col] = f'<td class="metric-best">{styled_table.loc[best_strategy, col]}</td>'

for col in ["Max Drawdown [%]"]:
    best_strategy = avg_metrics[col].idxmin()
    styled_table.loc[best_strategy, col] = f'<td class="metric-best">{styled_table.loc[best_strategy, col]}</td>'

# Формируем таблицу вручную
table_html = "<table><tr><th>Strategy</th>"
for col in styled_table.columns:
    table_html += f"<th>{col}</th>"
table_html += "</tr>"

for idx, row in styled_table.iterrows():
    table_html += f"<tr><td>{idx}</td>"
    for col in styled_table.columns:
        cell = row[col]
        if isinstance(cell, str) and 'class="metric-best"' in cell:
            table_html += cell
        else:
            table_html += f"<td>{cell}</td>"
    table_html += "</tr>"
table_html += "</table>"

html_parts.append(table_html)

# === Завершаем HTML ===
html_parts.append("</body></html>")

# Сохраняем отчет
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(''.join(html_parts))

print(f"✅ HTML-отчет сохранён: {REPORT_PATH}")

# Автоматически открываем браузер
webbrowser.open('file://' + os.path.realpath(REPORT_PATH))

