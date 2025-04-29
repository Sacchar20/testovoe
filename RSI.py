"""from strategies.base_strategy import StrategyBase
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands


class RsiBbStrategy(StrategyBase):
    def __init__(self, data, rsi_period=14, bb_period=20, bb_std=2):
        super().__init__(data)
        self.rsi_period = rsi_period
        self.bb_period = bb_period
        self.bb_std = bb_std

    def generate_signals(self):
        close = self.data['close']

        rsi = RSIIndicator(close=close, window=self.rsi_period).rsi()
        bb = BollingerBands(close=close, window=self.bb_period, window_dev=self.bb_std)

        entries = (rsi < 30) & (close < bb.bollinger_lband())
        exits = (rsi > 70) & (close > bb.bollinger_hband())

        # ⏱️ Задержка входа/выхода на 1 минуту
        entries = entries.shift(1, fill_value=False)
        exits = exits.shift(1, fill_value=False)

        return entries, exits
"""


import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from strategies.base_strategy import StrategyBase

class RsiBbStrategy(StrategyBase):
    def __init__(self, data, rsi_period=14, bb_period=20, bb_std=2, **kwargs):
        super().__init__(data, **kwargs)
        self.rsi_period = rsi_period
        self.bb_period = bb_period
        self.bb_std = bb_std

    def generate_signals(self):
        close = self.data.xs('close', level=0, axis=1)  # <=== ДОБАВИТЬ ЭТУ СТРОКУ!

        entries = pd.DataFrame(False, index=close.index, columns=close.columns)
        exits = pd.DataFrame(False, index=close.index, columns=close.columns)

        for symbol in close.columns:
            rsi = RSIIndicator(close=close[symbol], window=self.rsi_period).rsi()
            bb = BollingerBands(close=close[symbol], window=self.bb_period, window_dev=self.bb_std)

            entries[symbol] = (rsi < 30) & (close[symbol] < bb.bollinger_lband())
            exits[symbol] = (rsi > 70) & (close[symbol] > bb.bollinger_hband())

        return entries, exits

