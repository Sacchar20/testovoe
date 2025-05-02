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



Стратегії

📈 1. SmaCrossoverStrategy
Стратегія перехрещення простих ковзних середніх (SMA) із фільтром ATR.
Стратегія генерує сигнал на покупку, коли короткострокова SMA перетинає довгострокову SMA знизу вгору, а волатильність (за ATR) перевищує певний поріг.
Сигнал на продаж виникає, коли короткострокова SMA перетинає довгострокову зверху вниз.
Додатково може використовуватися система тейк-профіту та трейлінг-стопу для управління ризиками та фіксації прибутку.

📉 2. RsiBbStrategy
Стратегія повернення до середнього значення на основі індикаторів RSI та смуг Боллінджера.
Сигнал на покупку генерується, коли RSI падає нижче 30, а ціна перебуває під нижньою смугою Боллінджера — що вказує на можливий стан перепроданості.
Сигнал на продаж з'являється, коли RSI піднімається вище 70, а ціна знаходиться над верхньою смугою Боллінджера — що вказує на можливу перекупленість.

📊 3. VwapReversionStrategy
Стратегія повернення до середнього значення з використанням середньозваженої ціни за обсягом (VWAP).
Сигнал на покупку виникає, коли ціна суттєво опускається нижче VWAP, з очікуванням повернення вгору.
Сигнал на продаж формується, коли ціна значно перевищує VWAP, з розрахунком на корекцію вниз.



Висновки

📊 Результати окремо по кожній стратегії
1. SMA Crossover Strategy
Total Return: -59.05% (!)

Win Rate: 16.83%

Max Drawdown: 59.05%

Sharpe Ratio: -80.53

Profit Factor: 0.23

Expectancy: -0.52

🔎 Висновок:
Стратегія провалилася. Величезні збитки, мізерна кількість виграшних угод (~17%), негативні метрики ефективності (Sharpe, Profit Factor).
Ця реалізація непрацездатна у даному вигляді — потрібно серйозно допрацьовувати фільтри, умови входу/виходу або підлаштовувати параметри SMA/ATR.


2. RSI + Bollinger Bands Strategy
Total Return: +33.50%

Win Rate: 52.61%

Max Drawdown: 14.87%

Sharpe Ratio: 16.66

Profit Factor: 1.50

Expectancy: 0.20

🔎 Висновок:
Стратегія показала хороший результат: позитивна дохідність, досить високий відсоток виграшних угод (>50%), прийнятний ризик (просадка < 15%).
Можна вважати її прибутковою і стійкою в поточних умовах без додаткової оптимізації. Але найбільший прибуток принесли пари з низькою ліквідністю, тому в реальності таких результатів не було б. СТратегія потребує більш детальних тестів 


3. VWAP Reversion Strategy
Total Return: +46.43%

Win Rate: 61.20%

Max Drawdown: 14.46%

Sharpe Ratio: 21.36

Profit Factor: 1.89

Expectancy: 0.45

🔎 Висновок:
Найкращий результат серед усіх трьох стратегій. Висока дохідність, хороша стабільність (більше 61% виграшних угод), дуже низька максимальна просадка і сильні метрики ризику/прибутку (Profit Factor близько 2).
Цю стратегію точно варто розвивати далі. Так само як і в минулій стратегіїї найбільший прибуток принесли пари з низькою ліквідністю, тому в реальності таких результатів не було б. СТратегія потребує більш детальних тестів 
