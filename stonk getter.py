# soup: https://realpython.com/beautiful-soup-web-scraper-python/
# rich: https://github.com/willmcgugan/rich
import sys
import string
import requests
import ctypes
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import box

console = Console(color_system="256")

TOTAL = None

style = "bold white on blue"
if len(sys.argv) < 2:
    user_input = input("Stocks to add (seperate with a comma): ")
    FILE = None
else:
    FILE = sys.argv[1]

table = Table(show_header=True, header_style="bold white")


def multi_replace(input_string: str, replacements: list):
    for replacement in replacements:
        input_string = input_string.replace(replacement, "")

    return input_string


def change_colour(value, good, bad):
    if "/" in value:
        return "N/A"
    if float(multi_replace(value, ["+", "-", "$"])) == 0:
        value = f"[bold grey]{multi_replace(value, ['+', '-'])}[/bold grey]"
    elif (float(multi_replace(value, ["+", "-", "$"]))
          > good and
          float(multi_replace(value, ["+", "-", "$"]))
          < bad):
        value = f"[bold green]{value}[/bold green]"
    else:
        value = f"[red]{value}[/red]"

    return value


class stock_info:

    def __init__(self, name):
        self.name = name
        self.status = None
        self.company_name = None
        self.price = None
        self.change = None
        self.change_pct = None
        self.volume = None
        self.avg_volume = None
        self.pe = None
        self.market_cap = None

    def get_stock_info(self):
        URL = f'https://www.marketwatch.com/investing/stock/{self.name.lower()}?mod=over_search'

        try:
            page = requests.get(URL)
        except ConnectionError:
            return

        soup = BeautifulSoup(page.content, 'html5lib')

        self.get_price(soup)

        for thing in soup.find_all('div', class_="element element--company"):
            self.company_name = thing.find('h1', class_="company__name").text

        self.get_status(soup)

        self.get_volume(soup)

        self.pe = self.extra_info(soup, 9)
        self.market_cap = self.extra_info(soup, 4)

    def get_status(self, soup):
        for thing in soup.find_all('div', class_="element element--intraday"):
            self.status = str(thing.find('div', class_="status").text
                              ).replace("\n", "")

    def extra_info(self, soup, i):
        try:
            return str(soup.find_all('li', class_="kv__item")
                       ).split('<li class="kv__item">'
                               )[i].split("</span>")[0].split(">")[-1]
        except:
            return "[red]error[/red]"

    def get_price(self, soup):
        for thing in soup.find_all('div', class_="intraday__data"):
            self.price = str(thing.find('h3', class_="intraday__price").text
                             ).replace("\n", "").strip()
            self.change = str(thing.find('span', class_="change--point--q"
                                         ).text
                              ).replace("\n", "")
            self.change_pct = str(thing.find('span', class_="change--percent--q"
                                             ).text
                                  ).replace("\n", "")

    def get_volume(self, soup):
        for thing in soup.find_all('div',
                                   class_="column column--full supportive-data"):
            self.volume = str(thing.find('span', class_="primary").text
                              ).replace("\n", "").split("Volume: ")[-1].strip()
            self.avg_volume = str(thing.find('span', class_="secondary").text
                                  ).split("Avg: ")[-1].strip()

    def prittify_info(self, data, first=False):
        self.get_stock_info()
        if self.price is not None:

            cn = self.company_name
            n = self.name
            p = self.price.translate({ord(c): None for c in string.whitespace})
            c = (('+' if float(self.change) > 0 else '-')
                 + '$' + self.change.replace("-", ""))
            pct = (('+' if float(self.change_pct.replace("%", "")) > 0 else '-')
                   + self.change_pct.replace("-", ""))

            temp_comp_name, temp_name, temp_price, temp_change, temp_pct_change, temp_vol, temp_avg_vol, temp_pe, market_cap = self.create_temp(cn, n, p, c, pct)

            if temp_pe != "N/A" and "error" not in temp_pe:
                temp_pe = change_colour(temp_pe, 0, 50)

            if float(self.change) > 0:
                temp_change = f"[bold green]{temp_change}[/bold green]"
            elif float(self.change) == 0:
                temp_change = f"[bold grey]{multi_replace(temp_change, ['+', '-'])}[/bold grey]"
            else:
                temp_change = f"[red]{temp_change}[/red]"

            if float(self.change_pct.replace("%", "")) > 0:
                temp_pct_change = f"[bold green]{temp_pct_change}[/bold green]"
            elif float(self.change_pct.replace("%", "")) == 0:
                temp_pct_change = f"[bold grey]{multi_replace(temp_pct_change, ['+', '-'])}[/bold grey]"
            else:
                temp_pct_change = f"[red]{temp_pct_change}[/red]"

            if "T" in market_cap:
                market_cap = f"[pale_green1]{market_cap}[/pale_green1]"

            data.append((temp_comp_name,
                         temp_name,
                         temp_price,
                         temp_change,
                         temp_pct_change,
                         temp_vol,
                         temp_avg_vol,
                         temp_pe,
                         market_cap,
                         f"[cyan]{self.status}[/cyan]"))

            if first:
                console.show_cursor(False)
                console.print(f"({len(data)}/{TOTAL}) Downloaded data for [green]{temp_name}          ", end="\r")

            return data
        return None, None, None, None, None, None, None, None, None

    def create_temp(self, cn, n, p, c, pct):
        temp_comp_name = f"[bright_white]{cn}"
        temp_name = n.upper()
        temp_price = str(p)
        temp_change = str(c)
        temp_pct_change = str(pct)
        temp_vol = f"[bright_yellow]{self.volume}[/bright_yellow]"
        temp_avg_vol = f"[yellow]{self.avg_volume}[/yellow]"
        temp_pe = self.pe.replace(",", "")
        market_cap = self.market_cap
        return temp_comp_name, temp_name, temp_price, temp_change, temp_pct_change, temp_vol, temp_avg_vol, temp_pe,market_cap

    def __repr__(self) -> str:
        return self.name


if FILE is None:
    if ".txt" in user_input:
        stocks_to_get = [x.upper() for x in open(user_input, "r").read().split("\n")]
    else:
        stocks_to_get = user_input.translate(
            {ord(c): None for c in string.whitespace}).split(",")
else:
    in_file = open(FILE, "r").read()
    
    if ", " in in_file:
        stocks_to_get = [x.upper() for x in in_file.split(", ")]
    else:
        stocks_to_get = [x.upper() for x in in_file.split("\n")]



    powershell_name = multi_replace(FILE, [".\\", ".txt"])

    try:
        ctypes.windll.kernel32.SetConsoleTitleW(f"{powershell_name} terminal")
    except AttributeError:
        print("Couldn't rename")

active = []


for stock in stocks_to_get:
    active.append(stock_info(stock.lower()))

active = list(set(active))

console.clear()
console.print(f"getting data for {stocks_to_get}")

TOTAL = len(stocks_to_get)


def multi_get_data(active, data, first, workers=20) -> list:
    with ThreadPoolExecutor(max_workers=workers) as executor:
        [executor.submit(v.prittify_info(data, first)) for v in active]

    return data


def remove_colours(value):
    return float(multi_replace(value, ["[bold green]",
                                       "[/bold green]",
                                       "[/red]",
                                       "[red]",
                                       "[bold grey]",
                                       "[/bold grey]"])[:-1])


def sort_data(active_stocks) -> list:
    full_values = {}
    just_pct = {}

    for i, value in enumerate(active_stocks):
        full_values[i] = value
        just_pct[i] = remove_colours(value[4])

    elements_byvalues = {key: just_pct[key] for key in sorted(just_pct,
                                                              key=just_pct.get,
                                                              reverse=True)}
    sorted_values = []

    for k, v in elements_byvalues.items():
        sorted_values.append(full_values[k])

    return sorted_values


def generate_table(first) -> Table:
    table = Table("Company name",
                  "Ticker",
                  "Price",
                  "Change",
                  "% Change",
                  "Volume",
                  "Avg Volume",
                  "P/E Ratio",
                  "Market Cap",
                  "Status",
                  show_header=True,
                  header_style="bold white",
                  show_lines=True,
                  box=box.SIMPLE_HEAVY)

    table.border_style = "grey66"

    values = []
    values = sort_data(multi_get_data(active, values, first))

    avg_val = []

    for value in values:
        cn, n, p, c, pct, v, avg, pe, mc, s = value

        removed_colours = remove_colours(pct)
        removed_symbol = str(removed_colours).replace("%", "")
        avg_val.append(float(removed_symbol))

        table.add_row(cn, n, p, c, pct, v, avg, pe, mc, s)

    if len(values) > 5:
        average_pct = str(round(sum(avg_val) / len(avg_val), 3))

        if round(sum(avg_val) / len(avg_val), 3) == 0:
            average_pct = "[white]" + average_pct + "%"
        elif round(sum(avg_val) / len(avg_val), 3) < 0:
            average_pct = "[red]" + average_pct + "%"
        elif round(sum(avg_val) / len(avg_val), 3) > 0:
            average_pct = "[green]" + "+" + average_pct + "%"

        table.add_row(None)

        table.add_row("Average % Change",
                      None, None, None,
                      average_pct,
                      None, None, None, None)

    return table


old_table = None
first = True

try:
    with Live(auto_refresh=False, vertical_overflow="ellipsis") as live:
        while True:
            new_table = generate_table(first)
            if old_table != new_table:
                if first:
                    console.clear()
                    first = False
                live.update(new_table)
                live.refresh()
                old_table = new_table
                console.show_cursor(False)

except KeyboardInterrupt:
    console.clear()
    console.print("[green]Closing...")
