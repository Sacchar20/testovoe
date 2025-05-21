"""# run_backtests.py




from strategies.sma import SmaCrossoverStrategy
from strategies.RSI import RsiBbStrategy
from strategies.WRAP import VwapReversionStrategy
from core.backtester import run_strategy_on_all_pairs
import pandas as pd
import os

def main():
    os.makedirs("results", exist_ok=True)  # ✅ создаёт results/, если нет

    print("\n📦 Загрузка данных...")
    df = pd.read_parquet("data/historical_data.parquet")
    df.columns = df.columns.str.lower()  # ✅ lowercase для всех колоно


    # Группируем по символу
    data = {
        symbol: group.assign(open_time=pd.to_datetime(group['open_time'], unit='ms')).set_index('open_time')
        for symbol, group in df.groupby("symbol")
    }

    print(f"Загружено {len(data)} торговых пар\n")

     # ========== SMA Crossover ==========
    print("🚀 Запуск SMA Crossover...")
    sma_results = run_strategy_on_all_pairs(SmaCrossoverStrategy, data)
    sma_results.to_csv("results/sma_results.csv")
    print("📈 Топ-10 пар по доходности (SMA):")
    print(sma_results["Total Return (%)"].sort_values(ascending=False).head(10))
    print("✅ SMA Crossover завершена\n")
    #
    # ========== RSI + BB ==========
    print("🚀 Запуск RSI + Bollinger Bands...")
    rsi_results = run_strategy_on_all_pairs(RsiBbStrategy, data)
    rsi_results.to_csv("results/rsi_bb_results.csv")
    print("📈 Топ-10 пар по доходности (RSI + BB):")
    print(rsi_results["Total Return (%)"].sort_values(ascending=False).head(10))
    print("✅ RSI + BB завершена\n")

    # ========== VWAP Reversion ==========
    print("🚀 Запуск VWAP Reversion...")
    vwap_results = run_strategy_on_all_pairs(VwapReversionStrategy, data)
    vwap_results.to_csv("results/vwap_results.csv")
    print("📈 Топ-10 пар по доходности (VWAP):")
    print(vwap_results["Total Return (%)"].sort_values(ascending=False).head(10))
    print("✅ VWAP Reversion завершена\n")

    print("\n🏁 Все бектесты завершены. Результаты сохранены в папке results/")

if __name__ == "__main__":
    main()
"""

import os
import pandas as pd
import logging
from strategies import STRATEGIES
from core.backtester import run_multi_strategy

# === Настройка логгера ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def collect_stats_by_symbol(pf, filename_prefix: str):
    if pf is None:
        print(f"⚠️ Портфель для стратегии {filename_prefix.upper()} не был создан.")
        return

    stats = pf.stats()
    stats.to_csv(f"results/{filename_prefix}_stats.csv")

    if "Total Return [%]" in stats.index:
        print(f"\n📈 Доходность по стратегии ({filename_prefix.upper()}): {stats['Total Return [%]']:.2f}%")
        print(f"\n📊 Все метрики по стратегии {filename_prefix.upper()}:")
        print(stats.round(2))
    else:
        print(f"\n⚠️ В stats нет метрики 'Total Return [%]'. Доступные метрики: {stats.index.tolist()}")


def save_trades(pf, filename_prefix: str):
    if pf is None:
        print(f"⚠️ Портфель для {filename_prefix.upper()} не создан, трейды не сохраняем.")
        return

    trades_df = pf.trades.records_readable
    os.makedirs("results/trades", exist_ok=True)
    trades_df.to_csv(f"results/trades/{filename_prefix}_trades.csv", index=False)
    print(f"💾 Трейды для {filename_prefix.upper()} сохранены в results/trades/{filename_prefix}_trades.csv")


def load_data():
    path = "data/historic_data.parquet"

    try:
        df = pd.read_parquet(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"❌ Файл {path} не найден. Сначала запусти скрипт загрузки данных.")

    # Проверим, есть ли нужные колонки
    expected_columns = ["open_time", "symbol"]
    for col in expected_columns:
        if col not in df.columns:
            raise ValueError(f"❌ Колонка '{col}' не найдена в DataFrame")

    # Преобразуем open_time в datetime (на всякий случай)
    df["open_time"] = pd.to_datetime(df["open_time"], errors="coerce")

    # Удаляем строки, где нет времени или символа
    df = df.dropna(subset=["open_time", "symbol"])

    # Устанавливаем MultiIndex
    df = df.set_index(["open_time", "symbol"]).sort_index()

    # Логирование диапазона
    min_time = df.index.get_level_values("open_time").min()
    max_time = df.index.get_level_values("open_time").max()
    logging.info(f"📅 Дата начала: {min_time}")
    logging.info(f"📅 Дата конца: {max_time}")

    return df



def run_strategy(strategy, df):
    print(f"🚀 Запуск {strategy.name.upper()}...")
    pf = run_multi_strategy(strategy, df)
    collect_stats_by_symbol(pf, strategy.name)
    save_trades(pf, strategy.name)
    print(f"✅ {str(strategy)} завершена\n")


def main():
    df = load_data()
    for strategy in STRATEGIES:
        run_strategy(strategy, df)


if __name__ == "__main__":
    main()

