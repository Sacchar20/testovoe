"""from abc import ABC, abstractmethod
import vectorbt as vbt


class StrategyBase(ABC):
    def __init__(self, data):
        self.data = data
        self.portfolio = None

    @abstractmethod
    def generate_signals(self):
        pass

    def run_backtest(self):
        price = self.data['close']
        entries, exits = self.generate_signals()

        # Добавим задержку (если не добавлена в стратегии)
        entries = entries.shift(1, fill_value=False)
        exits = exits.shift(1, fill_value=False)

        self.portfolio = vbt.Portfolio.from_signals(
            price,
            entries=entries,
            exits=exits,
            init_cash=1000.0,
            size_type='percent',  # 💰 Используем долю от капитала
            size=0.10,  # 🔒 Только 10% на сделку
            fees=0.001,
            slippage=0.005,
            freq="1min"
        )

    def get_metrics(self):
        if self.portfolio is None:
            raise RuntimeError("run_backtest must be called first")
        stats = self.portfolio.stats()

        def safe_get(key):
            return stats[key] if key in stats else None


        return {
            "Total Return (%)": safe_get("Total Return [%]"),
            "Sharpe Ratio": safe_get("Sharpe Ratio"),
            "Max Drawdown (%)": safe_get("Max Drawdown [%]"),
            "Win Rate (%)": safe_get("Win Rate [%]"),
            "Expectancy": safe_get("Expectancy"),
            "Total Trades": safe_get("Total Trades")
        }
"""

# base_strategy.py
from abc import ABC, abstractmethod
import vectorbt as vbt

class StrategyBase(ABC):
    def __init__(self, data, position_size=0.01):
        self.data = data  # DataFrame с мультиколонками (symbol1, symbol2, ...)
        self.portfolio = None
        self.position_size = position_size

    @abstractmethod
    def generate_signals(self):
        pass

    def run_backtest(self):
        price = self.data.xs('close', axis=1, level=0)
        entries, exits = self.generate_signals()

        # Очистим NaN и проверим, есть ли хоть один True
        entries = entries.fillna(False)
        exits = exits.fillna(False)

        if not entries.any().any() and not exits.any().any():
            print("⚠️ Нет сигналов входа/выхода. Пропускаем стратегию.")
            self.portfolio = None
            return

        # Задержка
        entries = entries.shift(1, fill_value=False)
        exits = exits.shift(1, fill_value=False)

        # Создаём портфель
        self.portfolio = vbt.Portfolio.from_signals(
            price,
            entries,
            exits,
            init_cash=10_000,
            size_type='percent',
            size=self.position_size,
            fees=0.001,
            slippage=0.001,
            freq="1min",
            cash_sharing=True
        )



    def get_metrics(self):
        if self.portfolio is None:
            raise RuntimeError("Сначала нужно запустить run_backtest")

        stats = self.portfolio.stats()
        return {
            "Total Return (%)": stats.loc["Total Return [%]"],
            "Sharpe Ratio": stats.loc["Sharpe Ratio"],
            "Max Drawdown (%)": stats.loc["Max Drawdown [%]"],
            "Win Rate (%)": stats.loc["Win Rate [%]"],
            "Expectancy": stats.loc["Expectancy"],
            "Total Trades": stats.loc["Total Trades"]
        }
