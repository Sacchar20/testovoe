import os
import requests
import zipfile
import pandas as pd
from io import BytesIO
from binance.client import Client
from tqdm import tqdm
import logging

# === Конфигурация ===
API_KEY = ""
API_SECRET = ""

MONTH = "2025-02"
INTERVAL = "1m"
BASE_URL = "https://data.binance.vision/data/spot/monthly/klines"
TEMP_DIR = "temp_downloads"
OUTPUT_PARQUET = "../data/historic_data.parquet"
TOP_N = 100
LOG_FILE = "../../data_download.log"

# === Логирование ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# === Binance API: получить BTC-пары ===
def get_btc_pairs():
    client = Client(API_KEY, API_SECRET)
    info = client.get_exchange_info()
    btc_pairs = [s['symbol'] for s in info['symbols'] if s['quoteAsset'] == 'BTC' and s['status'] == 'TRADING']
    logging.info(f"🔍 Найдено {len(btc_pairs)} BTC-пар")
    return btc_pairs

# === Скачивание ZIP с кешированием ===
def download_and_extract(symbol):
    zip_filename = f"{symbol}-{INTERVAL}-{MONTH}.zip"
    local_zip_path = os.path.join(TEMP_DIR, zip_filename)

    if os.path.exists(local_zip_path):
        logging.info(f"📦 Кеш найден: {zip_filename}")
    else:
        url = f"{BASE_URL}/{symbol}/{INTERVAL}/{zip_filename}"
        try:
            logging.info(f"⬇️ Скачиваем: {url}")
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            with open(local_zip_path, "wb") as f:
                f.write(response.content)
            logging.info(f"✅ Сохранено: {local_zip_path}")
        except Exception as e:
            logging.warning(f"❌ {symbol}: ошибка при скачивании — {e}")
            return None

    # Распаковка CSV
    try:
        with zipfile.ZipFile(local_zip_path, 'r') as zf:
            extracted_file = zf.namelist()[0]
            zf.extractall(TEMP_DIR)
            return os.path.join(TEMP_DIR, extracted_file)
    except Exception as e:
        logging.error(f"❌ {symbol}: ошибка при распаковке — {e}")
        return None

# === Преобразование CSV в DataFrame ===
def process_csv(filepath, symbol):
    df = pd.read_csv(filepath, header=None)
    df.columns = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ]
    df["symbol"] = symbol
    df = df.drop(columns=["ignore"])

    # Приведение к миллисекундам, если данные в наносекундах
    if df['open_time'].max() > 1e15:
        df['open_time'] = df['open_time'] // 1_000_000
        df['close_time'] = df['close_time'] // 1_000_000
        logging.info(f"{symbol}: время переведено из наносекунд в миллисекунды")

    return df


# === Главная функция ===
def download_btc_data():
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_PARQUET), exist_ok=True)

    symbols = get_btc_pairs()
    pair_data = {}
    volumes = {}

    for symbol in tqdm(symbols, desc="Загрузка и обработка"):
        path = download_and_extract(symbol)
        if not path:
            continue

        df = process_csv(path, symbol)
        if df.empty:
            continue

        volume = df["volume"].astype(float).sum()
        volumes[symbol] = volume
        pair_data[symbol] = df

    # Топ по объёму
    top_symbols = sorted(volumes, key=volumes.get, reverse=True)[:TOP_N]
    logging.info(f"📈 Топ-{TOP_N} по объёму: {top_symbols}")

    top_dfs = [pair_data[s] for s in top_symbols if s in pair_data]
    if top_dfs:
        final_df = pd.concat(top_dfs)
        final_df.to_parquet(OUTPUT_PARQUET, engine="pyarrow", compression="snappy")
        logging.info(f"✅ Сохранено в: {OUTPUT_PARQUET}")
    else:
        logging.warning("❌ Ни одна пара не была успешно обработана.")

# === Запуск вручную ===
if __name__ == "__main__":
    download_btc_data()
