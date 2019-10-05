import pickle
import requests
import xml.etree.ElementTree as ET

"""
line 9 to line 51 just for using currency data
"""

class currency_data:
	def __init__(self, currency_name = None, renew_date = None, history = list()):
		self.currency_name = currency_name
		self.history = list(history)
		self.renew_date = renew_date

	def get_table(self, url):
		response = requests.get(url)
		text = response.content.decode('utf-8')
		start = text.find('<table')
		end = text.find('</table>') + 8
		return text[start : end]

	def get_history(self, url, renew_date):
		counter = 1
		#self.history = list()
		ok = True
		while ok:
			table = self.get_table(url + '%s&page=%d' %(self.currency_name ,counter))
			tree = ET.fromstring(table)
			rows = list(tree[0][1:])
			if not rows:
				break
			for row in rows:
				grids = list(row)
				date = grids[0][0].text
				buy = float(grids[3].text)
				sell = float(grids[4].text)
				if(date == renew_date):
					ok = False
					break
				self.history.append((date, buy, sell))
			counter += 1
	
	def upload(self, new_history):
		self.history = new_history.history + self.history

	def renew(self):
		print('now ', self.history[0][0])
		self.renew_date = self.history[0][0]

	def call_data(self):
		return self.history

class asset_allocation:
	def __init__(self, date , country = list(), currency_set = {}):
		self.date = date
		self.country = country
		self.currency_set = currency_set
		"""
		currency_set means how many % for every currency
		"""

class pnl():
	def __init__(self, asset, country, base):
		self.asset = list(asset)
		self.country = list(country)
		self.base = base
		Data = open("Currency.txt", "rb")
		now_Data = pickle.load(Data)
		Data.close()
		self.value = list()
		start = 0
		for x in range(0, len(now_Data['USD'].history)):
			if(now_Data['USD'].history[x][0] == asset[0].date):
				start = x
				break
		for x in range(0, len(asset)):
			now_date = asset[x].date
			now_value = 0
			if(x == 0):
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
		self.day_return = list()
		for x in range(0, len(asset)):
			self.day_return.append(float((self.value[x] - base) / base))

	def print_data(self, n):
		"""
		find the first n days' data 
		"""
		length = min(n, len(asset))
		for x in range(0, length):
			print(self.asset[x].date, ' ', self.value[x], ' ', self.day_return[x])


asset = list()
country = ['USD', 'JPY', 'AUD', 'SEK']
currency_set = [0.2, 0.2, 0.2, 0.4];
asset.append(asset_allocation('2019-09-26', country, currency_set))
currency_set = [0.2, 0.3, 0.2, 0.3];
asset.append(asset_allocation('2019-09-27', country, currency_set))
currency_set = [0.5, 0.2, 0.2, 0.1];
asset.append(asset_allocation('2019-09-30', country, currency_set))
currency_set = [0.6, 0.2, 0.2, 0.0];
asset.append(asset_allocation('2019-10-01', country, currency_set))
profit = pnl(asset, country, 10000)
profit.print_data(10)