import pandas as pd
import numpy as np
import pytest
from strategies.sma import SmaCrossoverStrategy
from strategies.RSI import RsiBbStrategy
from strategies.WRAP import VwapReversionStrategy

@pytest.fixture
def dummy_data():
    dates = pd.date_range("2025-02-01", periods=100, freq="1min")
    symbols = ["BTCUSDT", "ETHBTC"]
    fields = ["open", "high", "low", "close", "volume"]

    arrays = {}
    for symbol in symbols:
        for field in fields:
            arrays[(field, symbol)] = np.random.rand(len(dates))

    df = pd.DataFrame(arrays, index=dates)
    df.index.name = "open_time"
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=["field", "symbol"])
    return df

def test_sma_signals(dummy_data):
    strategy = SmaCrossoverStrategy(dummy_data)
    entries, exits = strategy.generate_signals()

    assert entries.shape == exits.shape
    assert entries.dtypes.unique().tolist() == [bool]
    assert exits.dtypes.unique().tolist() == [bool]

def test_rsi_signals(dummy_data):
    strategy = RsiBbStrategy(dummy_data)
    entries, exits = strategy.generate_signals()

    assert entries.shape == exits.shape
    assert entries.dtypes.unique().tolist() == [bool]
    assert exits.dtypes.unique().tolist() == [bool]

def test_vwap_signals(dummy_data):
    strategy = VwapReversionStrategy(dummy_data)
    entries, exits = strategy.generate_signals()

    assert entries.shape == exits.shape
    assert entries.dtypes.unique().tolist() == [bool]
    assert exits.dtypes.unique().tolist() == [bool]
