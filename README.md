Trading Strategy Backtester

A Python framework for designing, backtesting, and analyzing technical-analysis-based trading strategies. It supports popular indicators like SMA and RSI, integrates with Binance for historical data, and provides rich visualizations of your strategy's performance.



Features

Modular architecture: Easily add new strategies or indicators via base_strategy.py.

Built-in indicators: SMA and RSI implementations (sma.py, RSI.py).

Data loading: Fetch and preprocess historical price data from Binance (data_loader_upgraded.py).

Backtesting engine: Simulate trades and calculate performance metrics (backtester.py, metrics.py).

Visualization: Plot equity curves and indicator charts using Matplotlib, Seaborn, and Plotly.

Testing suite: Ensure reliability with unit tests (test_backtester.py, test_strategies.py).



Installation

Clone the repository:

git clone https://github.com/your-username/your-repo.git
cd your-repo

Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate       # Linux/macOS
# venv\Scripts\activate      # Windows PowerShell

Install dependencies:

pip install --upgrade pip
pip install -r requirements.txt



Usage

Configure your strategy in main.py:

Select indicator parameters (e.g., SMA period, RSI thresholds).

Set trading pair, timeframe, and date range.

Run the backtest:

python main.py

View results:

Performance metrics printed in console.

Charts and plots saved to the output/ folder.


Project Structure

project/
├── core/
│   ├── data_loader.py
│   ├── backtester.py
│   └── metrics.py
├── strategies/
│   ├── base_strategy.py
│   ├── sma.py
│   ├── rsi.py
│   └── wrap.py
├── tests/
│   ├── test_backtester.py
│   └── test_strategies.py
├── data/
│   └── historical_data.parquet
├── results/
│   ├── metrics.csv
│   └── screenshots/
│       └── strategy1_equity.png
├── main.py
├── requirements.txt
└── README.md



Running Tests

Execute the full test suite with pytest:

pytest



Contributing

Contributions are welcome! To contribute:

Fork the repository.

Create a feature branch (git checkout -b feature/YourFeature).

Commit your changes (git commit -m "Add feature").

Push to the branch (git push origin feature/YourFeature).

Open a Pull Request.

Please follow PEP8 and include tests for new functionality.
