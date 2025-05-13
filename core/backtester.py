"""import pandas as pd
import os
import matplotlib.pyplot as plt

def run_strategy_on_all_pairs(strategy_class, data_dict):
    results = []

    for symbol, df in data_dict.items():
        try:
            strat = strategy_class(df)
            strat.run_backtest()
            metrics = strat.get_metrics()
            metrics['Symbol'] = symbol
            results.append(metrics)

            # 🔽 Сохраняем портфель
            portfolio_dir = "results/portfolios"
            os.makedirs(portfolio_dir, exist_ok=True)
            pf_filename = f"{portfolio_dir}/{symbol.lower()}_{strategy_class.__name__.lower()}.pkl"
            strat.portfolio.save(pf_filename)

        except Exception as e:
            print(f"[ERROR] {symbol}: {e}")

    if results:
        return pd.DataFrame(results).set_index('Symbol')
    else:
        print("❌ Нет успешных результатов. Проверь данные.")
        return pd.DataFrame()




def save_results(df, filename):
    os.makedirs("..", exist_ok=True)
    df.to_csv(f"results/{filename}.csv")


def plot_equity(pf, filename):
    fig = pf.plot()
    fig.update_layout(title=filename)
    fig.write_image(f"results/{filename}.png")  # ← сохранить как PNG
"""




# backtester.py (обновлён под мультиформат)
import os
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import vectorbt as vbt

import os

def run_multi_strategy(strategy_class, df, position_size=0.01):
    """
    Запускает стратегию на мультиформатных данных и возвращает vbt.Portfolio.

    Аргументы:
        strategy_class: класс стратегии (должен быть подклассом StrategyBase)
        df: DataFrame с индексом (open_time, symbol)
        position_size: размер позиции в долях (по умолчанию 1%)

    Возвращает:
        vbt.Portfolio
    """
    import os

    # Преобразуем строки в MultiIndex-колонки (field, symbol)
    df_wide = df.unstack('symbol')

    # Инициализация стратегии
    strategy = strategy_class(df_wide, position_size=position_size)
    strategy.run_backtest()

    # Получаем объект портфеля
    pf = strategy.portfolio

    # Определяем имя стратегии
    strategy_name_map = {
        "smacrossoverstrategy": "sma",
        "rsibbstrategy": "rsi",
        "vwapreversionstrategy": "vwap"
    }

    class_name = strategy_class.__name__.lower()
    strat_name = strategy_name_map.get(class_name, class_name)

    # === Сохраняем стоимость портфеля (value), а не просто кэш
    value_df = pf.value()
    os.makedirs("results/cash", exist_ok=True)
    value_df.to_csv(f"results/cash/{strat_name}_cash.csv")

    return pf



def save_results(stats_df, filename):
    os.makedirs("results", exist_ok=True)
    stats_df.to_csv(f"results/{filename}.csv")


def plot_equity(pf, filename):
    equity = pf.asset_value()
    fig = go.Figure()

    if isinstance(equity, pd.DataFrame):
        for col in equity.columns:
            fig.add_trace(go.Scatter(x=equity.index, y=equity[col], mode='lines', name=str(col)))
    else:
        fig.add_trace(go.Scatter(x=equity.index, y=equity, mode='lines', name='Equity'))

    fig.update_layout(title=f"Equity Curve — {filename}", xaxis_title='Date', yaxis_title='Equity')

    # Сохраняем график
    try:
        fig.write_image(f"results/{filename}.png")
    except ValueError as e:
        print(f"⚠️ Не удалось сохранить график equity для {filename}: {e}")
        print("Убедитесь, что установлен пакет 'kaleido'. Установите его с помощью команды: pip install -U kaleido")




