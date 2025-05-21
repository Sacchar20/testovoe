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
    name = "vwap"
    """
    Стратегия возврата к VWAP для мультиактивного формата.

    Входит в позицию, если цена упала ниже VWAP на заданный порог.
    Выходит из позиции, если цена вернулась выше VWAP.

    Args:
        data (pd.DataFrame): Мультиформатный DataFrame с колонками уровня 'close' и 'volume'.
        threshold (float, optional): Порог отклонения от VWAP для входа в сделку. По умолчанию 0.005 (0.5%).
        **kwargs: Дополнительные параметры для базового класса StrategyBase.
    """

    def __init__(self, data, threshold=0.005, **kwargs):
        super().__init__(data, **kwargs)
        self.threshold = threshold

    def generate_signals(self):
        """
        Генерирует сигналы на вход и выход из сделок на основе отклонения от VWAP.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]:
                - entries: DataFrame сигналов на вход (True — входить в сделку).
                - exits: DataFrame сигналов на выход (True — выходить из сделки).
        """
        close = self.data.xs('close', level=0, axis=1)
        volume = self.data.xs('volume', level=0, axis=1)

        # Инициализация пустых таблиц сигналов
        entries = pd.DataFrame(False, index=close.index, columns=close.columns)
        exits = pd.DataFrame(False, index=close.index, columns=close.columns)

        # Проходим по каждому символу
        for symbol in close.columns:
            symbol_close = close[symbol]
            symbol_volume = volume[symbol]

            # Приводим индекс времени к дате для расчёта внутридневного VWAP
            day_index = symbol_close.index.get_level_values('open_time').normalize()

            # Считаем накопленную сумму "цена * объем" и объема
            cum_vol_price = (symbol_close * symbol_volume).groupby(day_index).cumsum()
            cum_vol = symbol_volume.groupby(day_index).cumsum()

            # Вычисляем VWAP
            vwap = cum_vol_price / cum_vol

            # Генерация сигналов:
            # Вход — цена ниже VWAP на порог
            entry_signal = symbol_close < vwap * (1 - self.threshold)

            # Выход — цена выше или равна VWAP
            exit_signal = symbol_close >= vwap

            # Сдвигаем сигналы на 1 бар вперёд (реакция на следующий бар)
            entries[symbol] = entry_signal.shift(1, fill_value=False)
            exits[symbol] = exit_signal.shift(1, fill_value=False)

        return entries, exits
