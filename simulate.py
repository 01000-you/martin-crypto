import random
import pandas as pd
import matplotlib.pyplot as plt
import logging
import datetime
import time

log = logging.getLogger()
logging.basicConfig(filename='consecutive.log', level=logging.INFO)


class StockSimulator:
    def __init__(self, data, buy_threshold, sell_threshold):
        self.data = data
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.commission_rate = 0.0005  # 0.05% 수수료
        self.balance = 100000000000
        self.stocks = 0
        self.total_trades = 0
        self.total_wins = 0
        self.total_lose = 0
        self.consecutive_losses = 0
        self.max_consecutive_losses = 0
        self.buy_price = None
        self.results = []  # 승패 결과를 기록하는 리스트
        self.list_max_consecutive_losses = []

    def simulate(self):
        for _ in range(random.randrange(1, 100)):
            self.data.pop(0)

        for idx, row in enumerate(self.data):
            _, _, start_price, high_price, low_price = row

            if self.stocks == 0:
                self.buy_stock(start_price)

            price_change_percent_win = (
                (high_price - self.buy_price) / self.buy_price) * 100
            price_change_percent_loss = (
                (low_price - self.buy_price) / self.buy_price) * 100

            if price_change_percent_win >= self.buy_threshold and price_change_percent_loss <= -self.sell_threshold:
                # random
                if random.randint(0, 1):
                    self.sell_stock_win(high_price, row)
                else:
                    self.sell_stock_lose(low_price)
            elif price_change_percent_win >= self.buy_threshold:
                self.sell_stock_win(high_price, row)
            elif price_change_percent_loss <= -self.sell_threshold:
                self.sell_stock_lose(low_price)
            else:
                self.results.append("No action")
                pass

            # self.print_simulation_status(idx)  # 현재 진행 상황 출력

    def print_simulation_status(self, idx):
        progress = (idx + 1) / len(self.data) * 100
        print(f"Progress: {progress:.2f}%")

    def buy_stock(self, price):
        if self.balance > price:
            self.stocks += 1
            self.balance -= price
            self.total_trades += 1
            self.buy_price = price
            # self.consecutive_losses = 0

    def sell_stock_win(self, price, row):
        if self.stocks > 0:
            self.balance += price * (1 - self.commission_rate)
            self.stocks = 0
            self.total_trades += 1
            self.total_wins += 1
            # self.list_max_consecutive_losses.append(self.consecutive_losses)
            self.list_max_consecutive_losses.append(
                [row[0], self.consecutive_losses])
            log.info(f'{row[0]}, {self.consecutive_losses}')
            self.consecutive_losses = 0
            self.results.append("Win")
        else:
            self.results.append("No action")

    def sell_stock_lose(self, price):
        if self.stocks > 0:
            self.balance += price * (1 - self.commission_rate)
            self.stocks = 0
            self.total_trades += 1
            self.total_lose += 1
            self.consecutive_losses += 1
            if self.consecutive_losses > self.max_consecutive_losses:
                self.max_consecutive_losses = self.consecutive_losses
            self.results.append("Lose")
        else:
            self.results.append("No action")

    def print_simulation_results(self):
        # print("\nSimulation Results:")
        # for idx, result in enumerate(self.results):
        #     print(f"Step {idx + 1}: {result}")
        print("Simulation completed.")
        print(f'총 데이터 개수 : {len(self.data)}')
        print(f"Total trades: {self.total_trades}")
        print(f"Total wins: {self.total_wins}")
        print(f"Total lose: {self.total_lose}")
        print(f"Max consecutive losses: {self.max_consecutive_losses}")

    def print_histogram(self):
        plt.hist(
            [item[1] for item in self.list_max_consecutive_losses], edgecolor='black', bins=100)
        plt.show()


data = []

################ load excel file ###################

start_time = time.time()
# xlsx 파일에서 데이터 읽어오기
# xlsx_file_path = 'dataset/BTC+분봉+데이터+100만건.xlsx'  # 파일 경로를 적절히 수정해주세요
# xlsx_file_path = 'dataset/BTC+수신데이터_subset.xlsx'  # 파일 경로를 적절히 수정해주세요
xlsx_file_path = 'dataset/BTC+수신데이터.xlsx'  # 파일 경로를 적절히 수정해주세요

# xlsx_data = pd.read_excel(xlsx_file_path)
xls = pd.ExcelFile(xlsx_file_path)
for sheet_name in xls.sheet_names:
    xlsx_data = pd.read_excel(xlsx_file_path, sheet_name=sheet_name)
    for _, row in xlsx_data.iterrows():
        timestamp = date = datetime.datetime.fromtimestamp(
            row['timestamp'] / 1e3)
        coin_symbol = row['코인종목']
        start_price = row['시작가']
        high_price = row['고가']
        low_price = row['저가']
        data.append((timestamp, coin_symbol,
                    start_price, high_price, low_price))

print(f'Loading time : {time.time() - start_time:.5f} sec')

# 시뮬레이션 실행
# sell_threshold = 0.94
# buy_threshold = 1.06
# sell_threshold = 0.24
# buy_threshold = 0.26

threshold = 1.0
commission = 0.06

sell_threshold = threshold - commission
buy_threshold = threshold + commission
magnification = 1
sell_threshold = sell_threshold * magnification
buy_threshold = buy_threshold * magnification


for i in range(10):
    simulator = StockSimulator(data, buy_threshold, sell_threshold)
    simulator.simulate()
    simulator.print_simulation_results()
    simulator.print_histogram()
