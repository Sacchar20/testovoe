"""import pandas as pd
from strategies.base_strategy import StrategyBase

class SmaCrossoverStrategy(StrategyBase):
    def __init__(self, data, fast_window=50, slow_window=200, tp_pct=0.05, trailing_pct=0.03):
        super().__init__(data)
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.tp_pct = tp_pct
        self.trailing_pct = trailing_pct

    def generate_signals(self):
        df = self.data.copy()
        close = df['close']
        fast_ma = close.rolling(self.fast_window).mean()
        slow_ma = close.rolling(self.slow_window).mean()

        entries = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))

        # Инициализируем Series сигналов выхода
        exits = pd.Series(False, index=close.index)

        in_position = False
        entry_price = 0
        trailing_stop = 0

        for i in range(1, len(df)):
            if entries.iloc[i]:
                in_position = True
                entry_price = close.iloc[i]
                trailing_stop = entry_price * (1 - self.trailing_pct)
                continue

            if in_position:
                price = close.iloc[i]

                # Обновляем трейлинг стоп
                new_trailing = price * (1 - self.trailing_pct)
                if new_trailing > trailing_stop:
                    trailing_stop = new_trailing

                # Условия выхода
                take_profit_hit = price >= entry_price * (1 + self.tp_pct)
                trailing_stop_hit = price <= trailing_stop

                if take_profit_hit or trailing_stop_hit:
                    exits.iloc[i] = True
                    in_position = False

        return entries, exits
"""

# strategies/sma.py

from strategies.base_strategy import StrategyBase
import pandas as pd


class SmaCrossoverStrategy(StrategyBase):
    name = "sma"

    def __init__(self, data, fast_window=50, slow_window=200, **kwargs):
        super().__init__(data, **kwargs)
        self.fast_window = fast_window
        self.slow_window = slow_window

    def generate_signals(self):
        close = self.data.xs('close', axis=1, level=0)
        fast_ma = close.rolling(self.fast_window).mean()
        slow_ma = close.rolling(self.slow_window).mean()

        entries = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
        exits = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))

        return entries, exits
