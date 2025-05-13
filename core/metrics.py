
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

# Установим рабочую директорию в корень проекта
os.chdir(os.path.dirname(os.path.dirname(__file__)))

# === Пути ===
RESULTS_DIR = "results"
TRADES_DIR = os.path.join(RESULTS_DIR, "trades")
CASH_DIR = os.path.join(RESULTS_DIR, "cash")
SCREENSHOTS_DIR = os.path.join(RESULTS_DIR, "screenshots")
REPORT_PATH = os.path.join(RESULTS_DIR, "report.html")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# === Стратегии (короткие имена) ===
strategies = ["sma", "rsi", "vwap"]

# === Загружаем метрики ===
metrics_list = []

for strat in strategies:
    stats_path = os.path.join(RESULTS_DIR, f"{strat}_stats.csv")
    print(f"🔍 Проверка: существует ли {stats_path}?")

    if not os.path.exists(stats_path):
        print(f"❌ Файл НЕ найден: {stats_path}")
        continue

    print(f"✅ Файл найден: {stats_path}")
    stats = pd.read_csv(stats_path, index_col=0).T
    stats["Strategy"] = strat

    for col in stats.columns:
        if col != "Strategy":
            stats[col] = pd.to_numeric(stats[col], errors="coerce")

    metrics_list.append(stats)

if not metrics_list:
    print("❌ Нет метрик для отчета.")
    exit()

metrics = pd.concat(metrics_list)

# === HTML блоки ===
html_parts = []

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

fig = go.Figure()

for strat in strategies:
    cash_path = os.path.join(CASH_DIR, f"{strat}_cash.csv")
    print(f"🔍 Проверка кеша: {cash_path}")
    if not os.path.exists(cash_path):
        print(f"⛔ Нет кеш-файла для {strat.upper()} по пути: {cash_path}")
        continue

    df = pd.read_csv(cash_path, index_col=0, parse_dates=True)

    if df.empty:
        print(f"⚠️ Пустой кеш-файл для {strat.upper()}")
        continue

    if isinstance(df, pd.DataFrame) and df.shape[1] == 1:
        series = df.iloc[:, 0]
    elif isinstance(df.columns, pd.MultiIndex):
        series = df.sum(axis=1)
    else:
        series = df.squeeze()

    series = pd.to_numeric(series, errors="coerce").dropna()

    if series.empty:
        print(f"⚠️ Пустая серия баланса для {strat.upper()}")
        continue

    fig.add_trace(go.Scatter(
        x=series.index,
        y=series.values,
        mode="lines",
        name=f"{strat.upper()} Strategy"
    ))

    # === Сохраняем PNG скриншот ===
    screenshot_path = os.path.join(SCREENSHOTS_DIR, f"strategy{strategies.index(strat)+1}_equity.png")
    fig.write_image(screenshot_path, width=1000, height=500)
    print(f"🖼 Сохранено изображение: {screenshot_path}")

fig.update_layout(
    title="Equity Curve по стратегиям",
    xaxis_title="Дата",
    yaxis_title="Баланс портфеля",
    height=500,
    yaxis=dict(tickformat=".0f")
)

html_parts.append(fig.to_html(full_html=False, include_plotlyjs=True))

# === 2. Heatmap по Total Return ===
html_parts.append("<h2>2. Heatmap по Total Return [%]</h2>")

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
styled_table = avg_metrics.round(2).astype("object").copy()

for col in ["Total Return [%]", "Win Rate [%]", "Profit Factor"]:
    if col in avg_metrics.columns:
        best_strategy = avg_metrics[col].idxmax()
        styled_table.loc[best_strategy, col] = f'<td class="metric-best">{styled_table.loc[best_strategy, col]}</td>'

for col in ["Max Drawdown [%]"]:
    if col in avg_metrics.columns:
        best_strategy = avg_metrics[col].idxmin()
        styled_table.loc[best_strategy, col] = f'<td class="metric-best">{styled_table.loc[best_strategy, col]}</td>'

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

# === Завершение ===
html_parts.append("</body></html>")

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(''.join(html_parts))

print(f"✅ HTML-отчет сохранён: {REPORT_PATH}")
webbrowser.open('file://' + os.path.realpath(REPORT_PATH))


