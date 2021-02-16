import requests
import json
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import box

FINNHUB_API = "c0j6pff48v6tlon08mf0"
TEST_API = "sandbox_c0j6pff48v6tlon08mfg"

console = Console()

pct_change = lambda x, y: abs(round(100 - (x / y) * 100, 2))


def to_dictionary(li: list) -> list:
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
    for k, d in data.items():
        if "error" in d:
            return None

    return_data = {}
    for k, d in data.items():
        return_data[f"[green]{k.upper()}"] = ("[cyan]" + str(d["c"]),
                                              calculate_pct(d["c"], d["pc"]),
                                              "[white]" + str(d["h"]),
                                              "[white]" + str(d["l"]),
                                              "[yellow]" + str(d["o"]),
                                              "[pale_green1]" + str(d["pc"]))
    return return_data


def calculate_pct(current_price: float, open_price: float) -> str:
    if current_price == open_price:
        return "[grey]0%"
    elif current_price > open_price:
        return f"[green]+{pct_change(current_price, open_price)}%"
    else:
        return f"[red]-{pct_change(current_price, open_price)}%"


def multi_replace(input_string: str, replacements: list):
    for replacement in replacements:
        input_string = input_string.replace(replacement, "")

    return input_string


def remove_colours(value):
    return float(multi_replace(value, ["[green]",
                                       "[red]",
                                       "[bold grey]"])[:-1])


def sort_data(data: dict) -> list:
    just_pct = {}

    for i, (k, v) in enumerate(data.items()):
        just_pct[k] = remove_colours(v[1])

    elements_byvalues = {key: just_pct[key] for key in sorted(just_pct,
                                                              key=just_pct.get,
                                                              reverse=True)}

    sorted_values = {}

    for k in elements_byvalues.keys():
        sorted_values[k] = data[k]

    return sorted_values


def generate_table(stg: dict) -> Table:
    table = Table("#",
                  "Ticker",
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

    stg = clean_data(get_table_data(stocks_to_get))

    if stg is None:
        return None

    stg = sort_data(stg)

    for i, (n, d) in enumerate(stg.items()):
        table.add_row(str(i + 1), n, d[0], d[1], d[2], d[3], d[4], d[5])

    return table


def display_table(stocks_to_get):
    try:
        with Live(auto_refresh=False, vertical_overflow="ellipsis") as live:
            while True:
                new_table = generate_table(stocks_to_get)
                if new_table is None:
                    console.print("API limit reached")
                else:
                    live.update(new_table)
                    live.refresh()
                    console.show_cursor(False)
                time.sleep(len(stocks_to_get))
    except KeyboardInterrupt:
        console.clear()
        console.print("[green]Closing...[/green]")


stocks_to_get = to_dictionary(["aapl",
                               "tsla",
                               "gme",
                               "nok",
                               "sne",
                               "sndl",
                               "pypl"])


display_table(stocks_to_get)
