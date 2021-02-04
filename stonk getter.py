#soup: https://realpython.com/beautiful-soup-web-scraper-python/

import os
import requests
from bs4 import BeautifulSoup
import time

clear = lambda: os.system('cls')

class stock_info:
    
    def __init__(self, name):
        self.name = name
        
        self.company_name = None
        self.price = None
        self.change = None
        self.change_pct = None

    def get_stock_info(self):
        URL = f'https://www.marketwatch.com/investing/stock/{self.name.lower()}?mod=over_search'
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, 'html.parser')

        price_html = (soup.find_all('div', class_="intraday__data"))

        for thing in price_html:
            
            self.price = str(thing.find('h3', class_="intraday__price").text).replace("\n", "")
            self.change = str(thing.find('span', class_="change--point--q").text
                        ).replace("\n", "")
            self.change_pct = str(thing.find('span', class_="change--percent--q").text
                            ).replace("\n", "")
        
        for thing in soup.find_all('div', class_="element element--company"):
            self.company_name = thing.find('h1', class_="company__name").text
        
        #return price_html, price, change, change_pct

    def return_stock_info(self):
        if self.price is not None:
            return self.company_name, self.name, self.price, ('+' if float(self.change) > 0 else '') + '$' + self.change, ('+' if float(self.change) > 0 else '') + self.change_pct
        else:
            return None

    def prittify_info(self):
        if self.price is not None:
            
            cn = self.company_name
            n = self.name
            p = self.price
            c = ('+' if float(self.change) > 0 else '-') + '$' + self.change.replace("-", "")
            pct = ('+' if float(self.change) > 0 else '-') + self.change_pct.replace("-", "")
            
            
            
            temp_comp_name = cn + ' ' * (40 - len(cn))
            temp_name = n + ' ' *  (8 - len(n))
            temp_price = str(p) + ' ' * (14 - len(str(p)))
            temp_change = str(c) + ' ' * (14 - len(str(c)))
            temp_pct_change = str(pct)# + ' ' * (14 - len(str(pct)))
            
            return temp_comp_name + "|" + temp_name.upper() + "|" + temp_price + "|" + temp_change + "|" + temp_pct_change + "|"
            

stocks_to_get = open("C:/Users/James Calnan/OneDrive - Trant Engineering Ltd/Desktop/test/web scraper/stocks.txt", "r").read().split("\n")

print(stocks_to_get)

oldtime = time.time()

active = []

for stock in stocks_to_get:
    active.append(stock_info(stock))



while True:

    #if time.time() - oldtime > 3:
    things = []
    time_take = time.time()
    print(f"\nGetting data...")
    for stock in active:
        stock.get_stock_info()
        things.append(stock.prittify_info())
    clear()
    oldtime = time.time()
    print("Company Name                            Stock    Price          Change         % Change\n" + "\n" + "-" * 87)
    for thing in things:
        print(f"{thing}" + "\n" + "-" * 87)
    print(f"Gathered in {round(time.time() - time_take)} seconds")
        
