import ccxt
import json
from Exchanges import BinanceExchange
from Utils import DataHelpers


class TradeGate():
    def __init__(self, configDict, exchangeName, spot=False, sandbox=False):
        exchangeClass = self.getCorrectExchange(exchangeName)
        if sandbox:
            self.apiKey = configDict['credentials']['test']['spot']['key']
            self.apiSecret = configDict['credentials']['test']['spot']['secret']

            self.exchange = exchangeClass(configDict['credentials']['test'], type='SPOT', sandbox=True)
        else:
            self.apiKey = configDict['credentials']['main']['spot']['key']
            self.apiSecret = configDict['credentials']['main']['spot']['secret']

            self.exchange = exchangeClass(configDict['credentials']['test'], type='SPOT', sandbox=False)

    def getBalance(self, asset=''):
        return self.exchange.fetchBalance(asset)

    def getSymbolTradeHistory(self, symbol):
        return self.exchange.SymbolTradeHistory(symbol)


    @staticmethod
    def getCorrectExchange(exchangeName):
        if exchangeName == 'Binance':
            return BinanceExchange.BinanceExchange

    def createAndTestOrder(self, symbol, side, orderType, quantity=None, price=None, timeInForce=None, stopPrice=None, icebergQty=None, newOrderRespType=None, recvWindow=None):
        currOrder = DataHelpers.OrderData(symbol.upper(), side.upper(), orderType.upper())

        if not quantity is None:
            currOrder.setQuantity(quantity)

        if not price is None:
            currOrder.setPrice(price)

        if not timeInForce is None:
            currOrder.setTimeInForce(timeInForce)

        if not stopPrice is None:
            currOrder.setStopPrice(stopPrice)

        if not icebergQty is None:
            currOrder.setIcebergQty(icebergQty)

        if not newOrderRespType is None:
            currOrder.setNewOrderRespType(newOrderRespType)
        
        if not recvWindow is None:
            currOrder.setRecvWindow(recvWindow)

        if not self.exchange.isOrderDataValid(currOrder):
            raise Exception('Incomplete data provided.')

        self.exchange.testOrder(currOrder)

        return currOrder

    def makeOrder(self, orderData):
        return self.exchange.makeOrder(orderData)

    def getSymbolOrders(self, symbol):
        return self.exchange.getSymbolOrders(symbol)

    def getOpenOrders(self, symbol=None):
        return self.exchange.getOpenOrders(symbol)

    def getTradingFees(self):
        return self.exchange.getTradingFees()

    def getSymbolAveragePrice(self, symbol):
        return self.exchange.getSymbolAveragePrice(symbol)
        
    def getSymbolLatestTrades(self, symbol, limit=None):
        return self.exchange.getSymbolLatestTrades(symbol, limit)

    def getSymbolTickerPrice(self, symbol):
        return self.exchange.getSymbolTickerPrice(symbol)

    def getSymbolKlines(self, symbol, interval, startTime=None, endTime=None, limit=None):
        return self.exchange.getSymbolKlines(symbol, interval, startTime, endTime, limit)

    def getExchangeTime(self):
        return self.exchange.getExchangeTime()