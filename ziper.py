import numpy as np
import matplotlib.pyplot as plt
from binance.client import Client
from binance.enums import *
import logging

# Вставьте ваш API ключ и секрет сюда
api_key = 'czs8NPf9uo1va2Sg4HB5NCWFO7XGNtP8RPHWLWU8eWqNw0XhqjCsPhJreJfaEMhv'
api_secret = 'v0Onk3jFT4G5Q4vufMt3eDqT2r2cKKW4NoOQC53uLNSfjRcBHfqdmYBrHaFa3Udx'

# Создание клиента Binance
client = Client(api_key, api_secret)

# Настройка логирования
logging.basicConfig(filename='trade_signals.log', level=logging.INFO, format='%(asctime)s %(message)s')

def get_historical_klines(symbol, interval, start_str):
    """Получение исторических данных"""
    klines = client.get_historical_klines(symbol, interval, start_str)
    return klines

def calculate_fibonacci_levels(data):
    """Расчет уровней Фибоначчи"""
    max_price = max(data)
    min_price = min(data)
    diff = max_price - min_price
    levels = {
        '0.0%': max_price,
        '23.6%': max_price - 0.236 * diff,
        '38.2%': max_price - 0.382 * diff,
        '50.0%': max_price - 0.5 * diff,
        '61.8%': max_price - 0.618 * diff,
        '100.0%': min_price
    }
    return levels

def find_trade_signals(data, levels, take_profit, stop_loss):
    """Поиск точек входа на основе уровней Фибоначчи"""
    signals = []
    for i in range(1, len(data)):
        if data[i-1] > levels['38.2%'] and data[i] <= levels['38.2%']:
            signals.append(('Buy', i))
        elif data[i-1] < levels['61.8%'] and data[i] >= levels['61.8%']:
            signals.append(('Sell', i))
    return signals

def plot_data(prices, signals, levels):
    """Построение графика цен и уровней Фибоначчи"""
    plt.figure(figsize=(14, 7))
    plt.plot(prices, label='Close Prices')
    
    for level, price in levels.items():
        plt.axhline(y=price, linestyle='--', alpha=0.5, label=f'Fibonacci {level}')

    buy_signals = [signal[1] for signal in signals if signal[0] == 'Buy']
    sell_signals = [signal[1] for signal in signals if signal[0] == 'Sell']
    plt.scatter(buy_signals, prices[buy_signals], marker='^', color='g', label='Buy Signal', alpha=1)
    plt.scatter(sell_signals, prices[sell_signals], marker='v', color='r', label='Sell Signal', alpha=1)
    
    plt.title('Price Chart with Fibonacci Levels and Trade Signals')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

def main():
    symbol = 'BTCUSDT'
    
    # Запрос пользователю выбора интервала времени
    interval_choice = input("Выберите интервал времени (1 - часовой, 2 - 15-минутный): ")
    if interval_choice == '1':
        interval = Client.KLINE_INTERVAL_1HOUR
        start_str = '1 day ago UTC'
    elif interval_choice == '2':
        interval = Client.KLINE_INTERVAL_15MINUTE
        start_str = '1 hour ago UTC'
    else:
        print("Неправильный выбор интервала времени. Используется часовой интервал.")
        interval = Client.KLINE_INTERVAL_1HOUR
        start_str = '1 day ago UTC'

    # Получение исторических данных
    klines = get_historical_klines(symbol, interval, start_str)
    close_prices = np.array([float(kline[4]) for kline in klines])

    # Рассчет уровней Фибоначчи
    fibonacci_levels = calculate_fibonacci_levels(close_prices)

    # Поиск точек входа
    signals = find_trade_signals(close_prices, fibonacci_levels, take_profit=0.05, stop_loss=0.03)

    # Вывод сигналов
    for signal in signals:
        message = f"Signal: {signal[0]} at index {signal[1]} (price: {close_prices[signal[1]]})"
        print(message)
        logging.info(message)

    # Расчет примерного расстояния, которое пройдет цена
    price_range = max(close_prices) - min(close_prices)
    print(f"Approximate price range: {price_range}")
    logging.info(f"Approximate price range: {price_range
