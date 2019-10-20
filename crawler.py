"""
Change history into dictionary
"""

import requests
import xml.etree.ElementTree as ET
import pickle

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
				if(date == renew_date):
					ok = False
					break
				buy = float(grids[3].text)
				sell = float(grids[4].text)
				if(self.currency_name is 'USD'):
					buy += 0.3
					sell -= 0.3
				else:
					buy *= 1.001
					sell *= 0.999
				"""
				Internet transaction discount
				"""
				self.history.append((date, buy, sell))
			counter += 1
	
	def upload(self, new_history):
		self.history = new_history.history + self.history

	def renew(self):
		print('now ', self.history[0][0])
		self.renew_date = self.history[0][0]

	def call_data(self):
		return self.history

if __name__ == '__main__':
	Country = ['USD', 'JPY', 'AUD', 'SEK', 'NZD', 'EUR', 'ZAR', 'GBP']
	url = 'https://historical.findrate.tw/his.php?c='
	Data = open("Currency.txt", "rb")
	now_Data = pickle.load(Data)
	Data.close()
	for country in Country:
		print(country)
		if(country not in now_Data):
			now_Data[country] = currency_data(country)
		history = currency_data(country, now_Data[country].renew_date)
		history.get_history(url, now_Data[country].renew_date)
		if(now_Data[country].renew_date):
			now_Data[country].upload(history)
		else:
			now_Data[country] = history
		now_Data[country].renew()
	Data = open("Currency.txt", 'wb')
	pickle.dump(now_Data, Data)
	Data.close()