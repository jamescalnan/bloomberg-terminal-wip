from rich.console import Console
import requests, json
from rich.table import Table
from rich.live import Live
from rich import box
import time

FINNHUB_API = "c0j6pff48v6tlon08mf0"
TEST_API = "sandbox_c0j6pff48v6tlon08mfg"

console = Console()


def key(input_key: str):
    return {"c":  "Current price",
            "h":  "High",
            "l":  "Low",
            "o":  "Open",
            "pc": "Previous close"}[input_key]


def to_dictionary(li: list) -> dict:
    return {x: None for x in li}


def query_api(current_stock: str):
    return json.loads(requests.get(
        f"https://finnhub.io/api/v1/quote?symbol={current_stock.upper()}&token={FINNHUB_API}"
        ).text)


def get_table_data(stg: dict):
    for key in stg.keys():
        stg[key] = query_api(key)
    return stg


def clean_data(data: dict) -> dict:
    return_data = {}
    for k, d in data.items():
        return_data[f"[green]{k.upper()}"] = ("[cyan]" + str(d["c"]),
                                              calculate_pct(d["c"], d["pc"]),
                                              "[white]" + str(d["h"]),
                                              "[white]" + str(d["l"]),
                                              "[yellow]" + str(d["o"]),
                                              "[pale_green1]" + str(d["pc"]))
    return return_data


def calculate_pct(current_price: float, open_price: float):
    if current_price == open_price:
        return "[grey]0%"
    elif current_price > open_price:
        return f"[green]+{abs(round(100 - (current_price / open_price) * 100, 2))}%"
    else:
        return f"[red]-{abs(round(100 - (current_price / open_price) * 100, 2))}%"


def generate_table(stg: dict) -> Table:
    table = Table("Ticker",
                  "Current Price",
                  "% Change",
                  "High",
                  "Low",
                  "Open",
                  "Previous Close",
                  show_header=True,
                  header_style="bold white",
                  show_lines=True,
                  box=box.SIMPLE_HEAVY)

    data = clean_data(get_table_data(stocks_to_get))

    for n, d in data.items():
        table.add_row(n, d[0], d[1], d[2], d[3], d[4], d[5])

    return table


stocks_to_get = to_dictionary(["aapl",
                               "tsla",
                               "gme",
                               "nok",
                               "sne",
                               "sndl",
                               "pypl"])


c = time.time()
console.print(generate_table(stocks_to_get))

console.print(f"\n\n{time.time() - c}")
