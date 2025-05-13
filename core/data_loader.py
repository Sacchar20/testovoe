import asyncio
import pandas as pd
import logging
import time
from binance import AsyncClient
import pyarrow
import os
from aiolimiter import AsyncLimiter

# ===== Конфигурация =====
API_KEY = ""
API_SECRET = ""
START_DATE = "1 Feb 2025"
END_DATE = "1 Mar 2025"
INTERVAL = AsyncClient.KLINE_INTERVAL_1MINUTE
BATCH_SIZE = 5
OUTPUT_FILE = "../../data/historical_data.parquet"
TOP_N = 100
limiter = AsyncLimiter(1200, 60)

# ===== Настройка логирования =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("../../data_download.log"),
        logging.StreamHandler()
    ]
)

# ===== Асинхронный сбор свечей =====
async def fetch_klines(client, symbol, interval, start_str, end_str, retries=3):
    """
    Загружает исторические свечи для одного символа с повторными попытками при ошибках.

    Args:
        client (AsyncClient): Асинхронный клиент Binance API.
        symbol (str): Торговая пара.
        interval (str): Таймфрейм свечей.
        start_str (str): Начальная дата в формате строки.
        end_str (str): Конечная дата в формате строки.
        retries (int): Количество попыток в случае ошибок. По умолчанию 3.

    Returns:
        Tuple[str, list]: Символ и список свечей (или пустой список при ошибках).
    """
    async with limiter:
        for attempt in range(1, retries + 1):
            try:
                klines = await client.get_historical_klines(symbol, interval, start_str, end_str)
                logging.info(f"{symbol}: получено {len(klines)} свечей")
                return symbol, klines
            except Exception as e:
                logging.warning(f"{symbol}: ошибка (попытка {attempt}): {e}")
                if attempt < retries:
                    await asyncio.sleep(10 * attempt)
                else:
                    logging.error(f"{symbol}: все попытки исчерпаны.")
                    return symbol, []

# ===== Главная логика =====
async def download_data():
    """
    Загружает исторические данные по всем BTC-парам с Binance.

    Returns:
        dict: Словарь {символ: список свечей}.
    """
    client = await AsyncClient.create(API_KEY, API_SECRET)
    try:
        info = await client.get_exchange_info()
        btc_pairs = [s['symbol'] for s in info['symbols'] if s['quoteAsset'] == 'BTC']
        logging.info(f"Найдено {len(btc_pairs)} BTC-пар")

        historical_data = {}

        for i in range(0, len(btc_pairs), BATCH_SIZE):
            batch = btc_pairs[i:i + BATCH_SIZE]
            logging.info(f"Обрабатываем пары: {batch}")
            tasks = [fetch_klines(client, s, INTERVAL, START_DATE, END_DATE) for s in batch]
            results = await asyncio.gather(*tasks)

            for symbol, klines in results:
                if klines:
                    historical_data[symbol] = klines

        return historical_data
    finally:
        await client.close_connection()

# ===== Обработка и сохранение данных =====
def process_and_save(historical_data):
    """
    Обрабатывает загруженные данные, фильтрует топовые пары по объёму и сохраняет в Parquet.

    Args:
        historical_data (dict): Словарь {символ: список свечей}.
    """
    symbol_volume = {
        symbol: sum(float(k[5]) for k in klines) for symbol, klines in historical_data.items()
    }

    top_symbols = sorted(symbol_volume, key=symbol_volume.get, reverse=True)[:TOP_N]
    logging.info(f"Топ-{TOP_N} пар по объёму: {top_symbols}")

    records = []
    for symbol in top_symbols:
        for k in historical_data[symbol]:
            records.append({
                'symbol': symbol,
                'open_time': int(k[0]),
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5]),
                'close_time': int(k[6]),
                'quote_asset_volume': float(k[7]),
                'number_of_trades': int(k[8]),
                'taker_buy_base_asset_volume': float(k[9]),
                'taker_buy_quote_asset_volume': float(k[10]),
            })

    output_dir = os.path.dirname(OUTPUT_FILE)
    os.makedirs(output_dir, exist_ok=True)
    df = pd.DataFrame(records)
    df.to_parquet(OUTPUT_FILE, engine="pyarrow", compression="snappy")
    logging.info(f"✅ Данные сохранены в {OUTPUT_FILE}")

# ===== Запуск =====
if __name__ == "__main__":
    """
    Точка входа в скрипт: загружает данные и сохраняет их в файл.
    Также измеряет и логирует время выполнения.
    """
    start_time = time.time()

    data = asyncio.run(download_data())
    process_and_save(data)

    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    logging.info(f"⏱ Время выполнения: {minutes} мин {seconds} сек")


