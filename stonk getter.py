#soup: https://realpython.com/beautiful-soup-web-scraper-python/
#rich https://rich.readthedocs.io/en/latest/reference/live.html?highlight=live
#https://rich.readthedocs.io/en/latest/live.html
#https://github.com/willmcgugan/rich
import os, sys
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.live import Live
import time

FILE = sys.argv[1]

console = Console()

table = Table(show_header=True, header_style="bold white")


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
            pct = ('+' if float(self.change_pct.replace("%", "")) > 0 else '-') + self.change_pct.replace("-", "")
            #[bold magenta]World[/bold magenta]
            
            temp_comp_name = cn
            temp_name = n.upper()
            temp_price = str(p)
            temp_change = str(c)
            temp_pct_change = str(pct)
            
            if float(self.change) > 0:
                temp_change = f"[bold green]{temp_change}[/bold green]"
            elif float(self.change) == 0:
                temp_change = f"[bold grey]{temp_change.replace('-', '').replace('+', '')}[/bold grey]"
            else:
                temp_change = f"[bold red]{temp_change}[/bold red]"
            
            if float(self.change_pct.replace("%", "")) > 0:
                temp_pct_change = f"[bold green]{temp_pct_change}[/bold green]"
            elif float(self.change_pct.replace("%", "")) == 0:
                temp_pct_change = f"[bold grey]{temp_pct_change.replace('-', '').replace('+', '')}[/bold grey]"
                
            else:
                temp_pct_change = f"[bold red]{temp_pct_change}[/bold red]"
            
            return temp_comp_name, temp_name, temp_price, temp_change, temp_pct_change
        return None, None, None, None, None
            

stocks_to_get = open(f"{FILE}", "r").read().split("\n")

console.print(stocks_to_get)

oldtime = time.time()

active = []

for stock in stocks_to_get:
    active.append(stock_info(stock))

console.clear()

def generate_table() -> Table:
    table = Table(show_header=True, header_style="bold white")

    table.add_column("Company name", style="dim")
    table.add_column("Stock")
    table.add_column("Price")
    table.add_column("Change")
    table.add_column("% Change")
    
    for stock in active:
        stock.get_stock_info()
        cn, n, p, c, pct = stock.prittify_info()
        if p is not None:
            table.add_row(cn, n, p, c, pct)
    
    return table
    
old_table = None

with Live(auto_refresh=False, vertical_overflow="ellipsis") as live:
    while True:
        new_table = generate_table()#for _ in range(12):
        if old_table != new_table:
            live.update(new_table)
            live.refresh()
            old_table = new_table
            

