# 📊 Trading Strategy Backtester!

A Python framework for designing, backtesting, and analyzing technical-analysis-based trading strategies.  
It supports popular indicators like SMA, RSI, VWAP, integrates with Binance, and generates rich HTML reports.

---

## 📈 Отчёт по стратегиям

[Открыть отчёт в браузере](https://sacchar20.github.io/testovoe/report.html)

---

## 🚀 Features

- 🧱 **Modular architecture**: Easily add new strategies via `base_strategy.py`
- 📉 **Built-in indicators**: SMA, RSI, VWAP implementations (`sma.py`, `rsi.py`, `wrap.py`)
- ⏳ **Data loading**: Fetch historical Binance data (`data_loader.py`)
- 🧪 **Backtesting engine**: Simulate trades and compute metrics (`backtester.py`)
- 📊 **Visualization**: Plot equity curves and metrics via Plotly/Matplotlib
- ✅ **Testing suite**: Run tests with `pytest` in `tests/`

---

## ⚙️ Installation

```bash
git clone https://github.com/Sacchar20/testovoe.git
cd testovoe

python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install --upgrade pip
pip install -r requirements.txt
```

---

## 💡 Usage

```bash
# 1. Загрузка данных
python core/data_loader.py

# 2. Запуск всех стратегий
python main.py
```

Все результаты сохраняются в папку `results/`, отчёт доступен по ссылке выше.

---

## 🗂 Project Structure

```
project/
├── core/
│   ├── data_loader.py
│   ├── backtester.py
│   ├── metrics.py
│   └── config.py
├── strategies/
│   ├── base_strategy.py
│   ├── SMA.py
│   ├── RSI.py
│   └── VWAP.py
├── docs/
│   └── report.html
├── results/
│   ├── trades/
│   │   └── *.csv
│   ├── top5_pairs_each_strategy/
│   │   └── *.png
│   ├── stats/
│   │   └── *.csv
│   └── heatmap.png
├── tests/
│   ├── test_backtester.py
│   └── test_strategies.py
├── main.py
├── requirements.txt
└── README.md
```

---

## 🧪 Running Tests

```bash
pytest
```

---

## 📊 Описание стратегий

### 1. **SmaCrossoverStrategy**  
Пересечение скользящих средних с ATR-фильтром.  
👎 *Результат*: **-58.11%**, Win Rate: 17.3%, Sharpe: -78.7  
🔎 *Вывод*: стратегия неработоспособна, требует доработки.

---

### 2. **RsiBbStrategy**  
RSI + Bollinger Bands.  
✅ *Результат*: **+19.87%**, Win Rate: 51.8%, Max DD: 15.8%, Sharpe: 10.0  
🔎 *Вывод*: стабильна, требует дополнительной фильтрации ликвидности. Почти вся прибыль заработана на "нереальных сделках". Нужно доработать стратегию и перепроверить на "реальных" парах. 

---

### 3. **VwapReversionStrategy**  
Отклонение от VWAP с возвратом.  
🥇 *Результат*: **+39.71%**, Win Rate: 61.99%, Max DD: 16.2%, Sharpe: 17.6  
🔎 *Вывод*: лучшая стратегия, стоит развивать дальше. Почти вся прибыль заработана на "нереальных сделках". Нужно доработать стратегию и перепроверить на "реальных" парах. 

---


