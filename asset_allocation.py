import pickle
import requests
import xml.etree.ElementTree as ET
from Crawler import currency_data

class asset_allocation:
	def __init__(self, date = None, country = list(), currency_set = {}):
		self.date = date
		self.country = country
		self.currency_set = currency_set
		"""
		currency_set means how many % for every currency
		"""

def call_alpha(start, end, now_Data, country_list):
	return_set = list()
	for x in range(start, end):
		today_set = list()
		for country in country_list:
			change = now_Data[country].history[x - 1][1] - now_Data[country].history[x - 2][1]
			change /= now_Data[country].history[x - 2][1]
			if(change < 0):
				today_set.append(-change)
			else:
				today_set.append(0.0)
		sum = 0
		for num in today_set:
			sum += num
		if(sum != 0):
			for num in range(0, len(today_set)):
				today_set[num] /= sum
		return_set.append(asset_allocation(now_Data[country].history[x][0], country_list, today_set))
	return return_set

class simulator():
	def __init__(self, country, base, asset = list()):
		self.asset = list(asset)
		self.country = list(country)
		self.base = base
		self.value = list()
		self.day_return = list()
		Data = open("Currency.txt", "rb")
		self.now_Data = pickle.load(Data)
		Data.close()

	def back_test(self, start, end):
		self.asset += call_alpha(start, end + 1, self.now_Data, self.country)
		# call_alpha will return an asset_allocation list

	def pnl(self):
		start = 0
		for x in range(0, len(self.now_Data['USD'].history)):
			if(self.now_Data['USD'].history[x][0] == self.asset[0].date):
				start = x
				break
		for x in range(0, len(self.asset)):
			now_date = self.asset[x].date
			now_value = 0
			if(x == 0):
				now_money = self.base
			else:
				now_money = self.value[x - 1]
			for y in range(0, len(self.country)):
				invest = now_money * self.asset[x].currency_set[y]
				now_value += float(invest * self.now_Data[self.country[y]].history[start][1] 
					                      / self.now_Data[self.country[y]].history[start][2])
				"""
					history[date][0] means date, [1] bank buy price, [2] bank sell price
				"""
			start += 1
			self.value.append(now_value)
		for x in range(0, len(self.asset)):
			self.day_return.append(float((self.value[x] - self.base) / self.base))

	def update(self, asset):
		self.asset += asset
		start = 0
		for x in range(0, len(now_Data['USD'].history)):
			if(now_Data['USD'].history[x][0] == asset[0].date):
				start = x
				break
		for x in range(0, len(asset)):
			now_date = asset[x].date
			now_value = 0
			if(len(self.value) == 0):
				now_money = self.base
			else:
				now_money = self.value[x - 1]
			for y in range(0, len(self.country)):
				invest = now_money * self.asset[x].currency_set[y]
				now_value += float(invest * now_Data[self.country[y]].history[start][1] / now_Data[self.country[y]].history[start][2])
				"""
					history[date][0] means date, [1] bank buy price, [2] bank sell price
				"""
			start += 1
			self.value.append(now_value)
			start = len(self.day_return)
		for x in range(start, len(self.asset)):
			self.day_return.append(float((self.value[x] - base) / base))
	
	def print_data(self):
		length = len(self.asset)
		for x in range(0, length):
			print(self.asset[x].date, ' ', self.value[x], ' ', self.day_return[x])

if __name__ == '__main__':
	country_list = ['USD', 'JPY', 'AUD', 'SEK', 'NZD', 'EUR', 'ZAR', 'GBP']
	future = simulator(country_list, 10000)
	future.back_test(0, 50)
	future.pnl()
	future.print_data()