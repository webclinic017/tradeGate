# Trade Gate
<div align="center">
    
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/RastinS/tradeGate/Run%20Unit%20Tests?label=Unit%20Tests&style=flat-square)
![PyPI](https://img.shields.io/pypi/v/TradeGate?style=flat-square)
![PyPI - Downloads](https://img.shields.io/pypi/dm/TradeGate)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/TradeGate?style=flat-square)
![GitHub](https://img.shields.io/github/license/rastins/tradegate?style=flat-square)

</div>

An algorithmic trading library to use as a gateway to different exchanges.

## How to install
Use this Github repository by running ```python setup.py install```, or using pip:
```bash
pip install TradeGate
```

## How to use
Use with a config file in JSON format. Your config file should look like this:
```json
{
    "Binance": 
    {
        "exchangeName": "Binance",
        "credentials": 
        {
            "main": 
            {
                "futures": 
                {
                    "key": "API-KEY",
                    "secret": "API-SECRET"
                },
                "spot": 
                {
                    "key": "API-KEY",
                    "secret": "API-SECRET"
                }
            },
            "test": 
            {
                "futures": 
                {
                    "key": "API-KEY",
                    "secret": "API-SECRET"
                },
                "spot": 
                {
                    "key": "API-KEY",
                    "secret": "API-SECRET"
                }
            }
        }
    }
}
```
You should read this config file as JSON and give the desired exchange information to the main class initializer. Use sandbox argument to connect to the testnets of exchanges (if it exists). This is shown below:
```python
from TradeGate import TradeGate
import json

with open('/path/to/config/file.json') as f:
    config = json.load(f)
    
gate = TradeGate(config['Binance'], sandbox=True)

print(gate.getSymbolTickerPrice('BTCUSDT'))
```
## Current Supported Exchanges
- Binance
- ByBit

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. The best way to contribute right now is to implement as many exchanges as possible. Make sure all test cases are passing.

## License
[MIT](https://choosealicense.com/licenses/mit/)
