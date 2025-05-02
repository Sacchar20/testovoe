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

def run_multi_strategy(strategy_class, df, position_size=0.01):
    """
    df — MultiIndex по строкам: (open_time, symbol)
    Преобразует его в MultiIndex по колонкам: (field, symbol)
    """
    # Перекидываем symbol с индекса в колонки
    df_wide = df.unstack('symbol')  # => MultiIndex columns: (field, symbol)

    strategy = strategy_class(df_wide, position_size=position_size)
    strategy.run_backtest()

    return strategy.portfolio



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




