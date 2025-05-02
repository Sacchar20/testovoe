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



from abc import ABC, abstractmethod
import vectorbt as vbt


class StrategyBase(ABC):
    """
    Абстрактный базовый класс для стратегий.

    Все пользовательские стратегии должны реализовать метод generate_signals().
    После генерации сигналов можно запускать бэктест с помощью run_backtest(),
    и затем извлекать метрики с помощью get_metrics().
    """

    def __init__(self, data, position_size=0.01):
        """
        Args:
            data (pd.DataFrame): Исторические данные с мультиколонками (уровень 0: 'close', 'volume', и т.д., уровень 1: symbol).
            position_size (float): Размер позиции в процентах от капитала (например, 0.01 для 1%).
        """
        self.data = data
        self.portfolio = None
        self.position_size = position_size

    @abstractmethod
    def generate_signals(self):
        """
        Метод генерации сигналов входа и выхода.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: entries и exits — булевы DataFrame одинаковой формы, где True = сигнал.
        """
        pass

    def run_backtest(self):
        """
        Запускает бэктест стратегии на основе сигналов.

        Создаёт объект vectorbt.Portfolio и сохраняет его в self.portfolio.
        """
        price = self.data.xs('close', axis=1, level=0)
        entries, exits = self.generate_signals()

        entries = entries.fillna(False)
        exits = exits.fillna(False)

        if not entries.any().any() and not exits.any().any():
            print("⚠️ Нет сигналов входа/выхода. Пропускаем стратегию.")
            self.portfolio = None
            return

        entries = entries.shift(1, fill_value=False)
        exits = exits.shift(1, fill_value=False)

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
        """
        Возвращает словарь ключевых метрик стратегии.

        Returns:
            dict: Метрики портфеля, включая доходность, Sharpe, просадку и т.д.

        Raises:
            RuntimeError: Если run_backtest не был вызван и портфель не создан.
        """
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

