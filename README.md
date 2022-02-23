# Trade Gate
[![PyPI version](https://img.shields.io/pypi/v/TradeGate.svg)](https://pypi.python.org/pypi/TradeGate)
[![Python version](https://img.shields.io/pypi/pyversions/TradeGate)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

:money_with_wings: An algorithmic trading library to use as a gateway to different exchanges

## How to install
Use this github repository and running ```python setup.py install```, or using pip:
```bash
pip install TradeGate
```

## How to use
Use with a config file in json format. Your config file should look like this:
```json
{
    "Binance": {
        "credentials": {
            "test": {
                "futures": {
                    "key": "API-KEY",
                    "secret": "API-SECRET"
                },
                "spot": {
                    "key": "API-KEY",
                    "secret": "API-SECRET"
                }
            }
        },
        "baseUrls": {
            "spot": "SPOT-URL",
            "futures": "FUTURES-URL"
        }
    }
}
```
You should read this config file as json and give the desired exchange's informations to the main class initializer. This is shown below:
```python
from TradeGate import TradeGate
import json

with open('/Users/rustinsoraki/Documents/Projects/tradeGate/config.json') as f:
    config = json.load(f)
    
gate = TradeGate(config['Binance'], 'Binance', sandbox=True)

print(gate.getSymbolTickerPrice('BTCUSDT'))
```
