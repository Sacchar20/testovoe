"""from strategies.base_strategy import StrategyBase
import pandas as pd


class VwapReversionStrategy(StrategyBase):
    def __init__(self, data, threshold=0.005):
        super().__init__(data)
        self.threshold = threshold

    def generate_signals(self):
        df = self.data.copy()

        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        day_index = df.index.normalize()

        df['cum_vol_price'] = (df['close'] * df['volume']).groupby(day_index).cumsum()
        df['cum_vol'] = df['volume'].groupby(day_index).cumsum()
        df['vwap'] = df['cum_vol_price'] / df['cum_vol']

        entries = df['close'] < df['vwap'] * (1 - self.threshold)
        exits = df['close'] >= df['vwap']

        # ⏱️ Задержка исполнения на 1 минуту
        entries = entries.shift(1, fill_value=False)
        exits = exits.shift(1, fill_value=False)

        return entries, exits
"""



# VwapReversionStrategy (мультиформат)
from strategies.base_strategy import StrategyBase
import pandas as pd

class VwapReversionStrategy(StrategyBase):
    def __init__(self, data, threshold=0.005, **kwargs):
        super().__init__(data, **kwargs)
        self.threshold = threshold

    def generate_signals(self):
        close = self.data.xs('close', level=0, axis=1)
        volume = self.data.xs('volume', level=0, axis=1)

        entries = pd.DataFrame(False, index=close.index, columns=close.columns)
        exits = pd.DataFrame(False, index=close.index, columns=close.columns)

        for symbol in close.columns:
            symbol_close = close[symbol]
            symbol_volume = volume[symbol]

            # Для VWAP нужна дата без времени
            day_index = symbol_close.index.get_level_values('open_time').normalize()

            cum_vol_price = (symbol_close * symbol_volume).groupby(day_index).cumsum()
            cum_vol = symbol_volume.groupby(day_index).cumsum()

            vwap = cum_vol_price / cum_vol

            entry_signal = symbol_close < vwap * (1 - self.threshold)
            exit_signal = symbol_close >= vwap

            entries[symbol] = entry_signal.shift(1, fill_value=False)
            exits[symbol] = exit_signal.shift(1, fill_value=False)

        return entries, exits


