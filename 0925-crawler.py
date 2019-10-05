"""
Change history into dictionary
"""

import requests
import xml.etree.ElementTree as ET
import pickle

class CurrencyData:
	def __init__(self, currency_name = None, renew_date = None, history = list()):
		self.currency_name = currency_name
		self.history = list(history)
		self.renew_date = renew_date

	def getTable(self, url):
		response = requests.get(url)
		text = response.content.decode('utf-8')
		start = text.find('<table')
		end = text.find('</table>') + 8
		return text[start : end]

	def getHistory(self, url, renew_date):
		counter = 1
		#self.history = list()
		ok = True
		while ok:
			table = self.getTable(url + '%s&page=%d' %(self.currency_name ,counter))
			tree = ET.fromstring(table)
			rows = list(tree[0][1:])
			if not rows:
				break
			for row in rows:
				grids = list(row)
				date = grids[0][0].text
				buy = grids[3].text
				sell = grids[4].text
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

	def callData(self):
		return self.history

if __name__ == '__main__':
	Country = ['USD', 'JPY', 'AUD', 'SEK']
	url = 'https://historical.findrate.tw/his.php?c='
	Data = open("Currency.txt", "rb")
	now_Data = pickle.load(Data)
	Data.close()
	for country in Country:
		print(country)
		if(country not in now_Data):
			now_Data[country] = CurrencyData(country)
		history = CurrencyData(country, now_Data[country].renew_date)
		history.getHistory(url, now_Data[country].renew_date)
		if(now_Data[country].renew_date):
			now_Data[country].upload(history)
		else:
			now_Data[country] = history
		now_Data[country].renew()
	Data = open("Currency.txt", 'wb')
	pickle.dump(now_Data, Data)
	Data.close()