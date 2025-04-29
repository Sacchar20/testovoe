"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

RESULTS_DIR = "../results"
SCREENSHOTS_DIR = os.path.join(RESULTS_DIR, "screenshots")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# ===== Загружаем метрики =====
strategies = {
    "sma": "sma_stats.csv",
    "rsi": "rsi_stats.csv",
    "vwap": "vwap_stats.csv"
}

all_metrics = []

for name, filename in strategies.items():
    path = os.path.join(RESULTS_DIR, filename)
    if not os.path.isfile(path):
        print(f"❌ Файл не найден: {path}")
        continue

    df = pd.read_csv(path)  # Убираем index_col="Symbol"
    df["strategy"] = name
    all_metrics.append(df)

# ===== Сравнение стратегий =====
if all_metrics:
    combined = pd.concat(all_metrics, ignore_index=True)

    # Средние значения по стратегиям
    avg = combined.groupby("strategy").mean(numeric_only=True)
    avg.to_csv(os.path.join(RESULTS_DIR, "metrics_summary.csv"))

    # Тепловая карта средних метрик
    plt.figure(figsize=(10, 6))
    sns.heatmap(avg, annot=True, fmt=".2f", cmap="coolwarm")
    plt.title("Средние метрики по стратегиям")
    plt.tight_layout()
    plt.savefig(os.path.join(SCREENSHOTS_DIR, "strategy_metrics_heatmap.png"))
    plt.close()

    print("✅ Метрики успешно сохранены и визуализированы.")
else:
    print("❌ Нет доступных метрик для анализа.")
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


