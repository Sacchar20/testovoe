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
from strategies.sma import SmaCrossoverStrategy
from strategies.RSI import RsiBbStrategy
from strategies.WRAP import VwapReversionStrategy
from core.backtester import run_multi_strategy, plot_equity

def collect_stats_by_symbol(pf, filename_prefix: str):
    """
    Собирает и сохраняет статистику по портфелю стратегии.

    Args:
        pf (vbt.Portfolio): Портфель, созданный после запуска стратегии.
        filename_prefix (str): Префикс для имени файла сохранения статистики.
    """
    if pf is None:
        print(f"⚠️ Портфель для стратегии {filename_prefix.upper()} не был создан.")
        return

    stats = pf.stats()

    # Сохраняем статистику
    stats.to_csv(f"results/{filename_prefix}_stats.csv")

    # Выводим топ-10 по доходности
    if "Total Return [%]" in stats.index:
        print(f"\n📈 Доходность по стратегии ({filename_prefix.upper()}): {stats['Total Return [%]']:.2f}%")
        print(f"\n📊 Все метрики по стратегии {filename_prefix.upper()}:")
        print(stats.round(2))
    else:
        print(f"\n⚠️ В stats нет метрики 'Total Return [%]'. Доступные метрики: {stats.index.tolist()}")

def save_trades(pf, filename_prefix: str):
    """
    Сохраняет сделки (trades) портфеля в CSV-файл.

    Args:
        pf (vbt.Portfolio): Портфель, созданный после запуска стратегии.
        filename_prefix (str): Префикс для имени файла сохранения трейдов.
    """
    if pf is None:
        print(f"⚠️ Портфель для {filename_prefix.upper()} не создан, трейды не сохраняем.")
        return

    trades_df = pf.trades.records_readable
    os.makedirs("results/trades", exist_ok=True)  # Папка для трейдов
    trades_df.to_csv(f"results/trades/{filename_prefix}_trades.csv", index=False)
    print(f"💾 Трейды для {filename_prefix.upper()} сохранены в results/trades/{filename_prefix}_trades.csv")

def main():
    """
    Основная функция запуска бэктеста для всех стратегий.

    Загружает данные, запускает стратегии SMA, RSI+BB и VWAP,
    сохраняет статистику и сделки по каждой стратегии.
    """
    os.makedirs("results", exist_ok=True)

    print("\n📦 Загрузка данных...")
    df = pd.read_parquet("data/historical_data.parquet")
    df.columns = df.columns.str.lower()
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df = df.set_index(['open_time', 'symbol']).sort_index()

    print(f"Загружено {df.index.get_level_values('symbol').nunique()} торговых пар\n")

    # ====== SMA ======
    print("🚀 Запуск SMA Crossover...")
    sma_pf = run_multi_strategy(SmaCrossoverStrategy, df)
    collect_stats_by_symbol(sma_pf, "sma")
    save_trades(sma_pf, "sma")
    print("✅ SMA Crossover завершена\n")

    # ====== RSI ======
    print("🚀 Запуск RSI + BB...")
    rsi_pf = run_multi_strategy(RsiBbStrategy, df)
    collect_stats_by_symbol(rsi_pf, "rsi")
    save_trades(rsi_pf, "rsi")
    print("✅ RSI + BB завершена\n")

    # ====== VWAP ======
    print("🚀 Запуск VWAP Reversion...")
    vwap_pf = run_multi_strategy(VwapReversionStrategy, df)
    collect_stats_by_symbol(vwap_pf, "vwap")
    save_trades(vwap_pf, "vwap")
    print("✅ VWAP Reversion завершена\n")

    print("\n🏁 Все бэктесты завершены. Результаты сохранены в папке results/")

if __name__ == "__main__":
    main()



