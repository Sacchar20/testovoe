import os
import pandas as pd
import numpy as np
import pytest
from unittest import mock
from core.backtester import run_multi_strategy, save_results, plot_equity
from strategies.sma import SmaCrossoverStrategy

@pytest.fixture
def dummy_df():
    dates = pd.date_range("2025-02-01", periods=100, freq="1min")
    symbols = ["BTCUSDT", "ETHBTC"]
    data = []

    for symbol in symbols:
        for i, dt in enumerate(dates):
            # Генерация колеблющейся цены (синусоида)
            price = 100 + np.sin(i / 5) * 5
            data.append({
                "open_time": dt,
                "symbol": symbol,
                "open": price - 0.5,
                "high": price + 0.5,
                "low": price - 1,
                "close": price,
                "volume": 1000
            })

    df = pd.DataFrame(data)
    df['open_time'] = pd.to_datetime(df['open_time'])
    df = df.set_index(['open_time', 'symbol'])
    return df


def test_run_multi_strategy_returns_portfolio(dummy_df):
    pf = run_multi_strategy(
        lambda data, position_size: SmaCrossoverStrategy(
            data, fast_window=5, slow_window=10, position_size=position_size
        ),
        dummy_df
    )
    assert pf is not None
    assert hasattr(pf, "stats")
    stats = pf.stats()
    assert isinstance(stats, (pd.Series, pd.DataFrame))


def test_save_results_creates_file(tmp_path):
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    test_file = tmp_path / "test_metrics.csv"

    save_results(df, test_file.stem)
    output_file = f"results/{test_file.name}"
    assert os.path.exists(output_file)
    os.remove(output_file)

@mock.patch("core.backtester.go.Figure.write_image")
def test_plot_equity_runs(mock_write_image, dummy_df):
    pf = run_multi_strategy(
        lambda data, position_size: SmaCrossoverStrategy(
            data, fast_window=5, slow_window=10, position_size=position_size
        ),
        dummy_df
    )
    if pf is None:
        pytest.skip("⚠️ Нет сигналов — портфель не создан.")
    plot_equity(pf, "test_equity")
    assert mock_write_image.called

