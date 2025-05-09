import pandas as pd
import io

def parse_tos(file):
    content = file.read().decode("utf-8")
    lines = content.splitlines()

    # Skip first 4 lines
    data_str = "\n".join(lines[4:])
    df = pd.read_csv(io.StringIO(data_str))

    df = df.rename(columns={
        'Instrument': 'symbol',
        'Qty': 'quantity',
        'Mark': 'current_price',
        'Cost Basis': 'cost_basis'
    })

    return df[['symbol', 'quantity', 'cost_basis', 'current_price']]


def parse_ibkr(file):
    df = pd.read_csv(file)
    df = df.rename(columns={
        'Symbol': 'symbol',
        'Quantity': 'quantity',
        'T. Price': 'cost_basis',
        'Market Price': 'current_price'
    })

    return df[['symbol', 'quantity', 'cost_basis', 'current_price']]


def parse_robinhood(file):
    df = pd.read_csv(file)
    df = df.rename(columns={
        'Symbol': 'symbol',
        'Quantity': 'quantity',
        'Cost Basis': 'cost_basis',
        'Price': 'current_price'
    })

    return df[['symbol', 'quantity', 'cost_basis', 'current_price']]