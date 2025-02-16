import json
import logging
import time

from binance.spot import Spot

from Exchanges.BaseExchange import BaseExchange
from TradeGates.Utils import BinanceHelpers
from binance_f import RequestClient
from binance_f.model.balance import Balance


class BinanceExchange(BaseExchange):
    timeIntervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w',
                     '1M']

    timeIndexesInCandleData = [0, 6]
    desiredCandleDataIndexes = [0, 1, 2, 3, 4, 5, 6, 8]

    spotOrderTypes = ['LIMIT', 'MARKET', 'STOP_LOSS', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT',
                      'TAKE_PROFIT_LIMIT', 'LIMIT_MAKER']

    futuresOrderTypes = ['LIMIT', 'MARKET', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET',
                         'TRAILING_STOP_MARKET']

    def __init__(self, credentials, sandbox=False, unifiedInOuts=True):
        self.credentials = credentials
        self.sandbox = sandbox
        self.unifiedInOuts = unifiedInOuts

        if sandbox:
            self.client = Spot(key=credentials['spot']['key'], secret=credentials['spot']['secret'],
                               base_url='https://testnet.binance.vision')
            self.futuresClient = RequestClient(api_key=credentials['futures']['key'],
                                               secret_key=credentials['futures']['secret'],
                                               url='https://testnet.binancefuture.com')
        else:
            self.client = Spot(key=credentials['spot']['key'], secret=credentials['spot']['secret'])
            self.futuresClient = RequestClient(api_key=credentials['futures']['key'],
                                               secret_key=credentials['futures']['secret'],
                                               url='https://fapi.binance.com')

        self.subFutureClient = None

    def getBalance(self, asset='', futures=False):
        if not futures:
            try:
                balances = self.client.account()['balances']
            except Exception:
                return None

            if asset == '':
                return balances
            else:
                for balance in balances:
                    if balance['asset'] == asset:
                        return balance
            return None
        else:
            balances = []
            for balance in self.futuresClient.get_balance():
                balances.append(balance.toDict())

            if asset == '':
                return balances
            else:
                for balance in balances:
                    if balance['asset'] == asset:
                        return balance
                return Balance.makeFreeBalance(asset)

    def symbolAccountTradeHistory(self, symbol, futures=False, fromId=None, limit=None):
        try:
            if not futures:
                return self.client.my_trades(symbol, fromId=fromId, limit=limit)
            else:
                trades = []
                for trade in self.futuresClient.get_account_trades(symbol=symbol, fromId=fromId, limit=limit):
                    trades.append(trade.toDict())
                return trades

        except Exception:
            return None

    def testSpotOrder(self, orderData):
        if not BinanceHelpers.isOrderDataValid(orderData):
            raise ValueError('Incomplete data provided.')

        orderData.setTimestamp()
        params = BinanceHelpers.getSpotOrderAsDict(orderData)

        response = self.client.new_order_test(**params)
        return response

    def makeSpotOrder(self, orderData):
        params = BinanceHelpers.getSpotOrderAsDict(orderData)

        response = self.client.new_order(**params)
        logging.info(response)
        return response

    def getSymbolOrders(self, symbol, futures=False, orderId=None, startTime=None, endTime=None, limit=None):
        try:
            if not futures:
                return self.client.get_orders(symbol, orderId=orderId, startTime=startTime, endTime=endTime,
                                              limit=limit, timestamp=time.time())
            else:
                orders = []
                for order in self.futuresClient.get_all_orders(symbol, orderId=orderId, startTime=startTime,
                                                               endTime=endTime, limit=limit):
                    orders.append(order.toDict())
                return orders
        except Exception:
            return None

    def getOpenOrders(self, symbol, futures=False):
        try:
            if not futures:
                return self.client.get_open_orders(symbol, timestamp=time.time())
            else:
                orders = []
                for order in self.futuresClient.get_open_orders(symbol=symbol):
                    orders.append(order.toDict())
                return orders
        except Exception:
            return None

    def cancelAllSymbolOpenOrders(self, symbol, futures=False):
        if not futures:
            openOrders = self.getOpenOrders(symbol)
            if len(openOrders) == 0:
                return []
            else:
                return self.client.cancel_open_orders(symbol, timestamp=time.time())
        else:
            openOrders = self.getOpenOrders(symbol, futures=True)

            if len(openOrders) == 0:
                return []
            else:
                orderIds = [order['orderId'] for order in openOrders]

                results = []
                for res in self.futuresClient.cancel_list_orders(symbol=symbol, orderIdList=orderIds):
                    results.append(res.toDict())

                return results

    def cancelOrder(self, symbol, orderId=None, localOrderId=None, futures=False):
        errorMessage = 'Specify either order Id in the exchange or local Id sent with the order'
        if not futures:
            if orderId is not None:
                return self.client.cancel_order(symbol, orderId=orderId, timestamp=time.time())
            elif localOrderId is not None:
                return self.client.cancel_order(symbol, origClientOrderId=localOrderId, timestamp=time.time())
            else:
                raise ValueError(errorMessage)
        else:
            if orderId is not None:
                return self.futuresClient.cancel_order(symbol, orderId=orderId).toDict()
            elif localOrderId is not None:
                return self.futuresClient.cancel_order(symbol, origClientOrderId=localOrderId).toDict()
            else:
                raise ValueError(errorMessage)

    def getOrder(self, symbol, orderId=None, localOrderId=None, futures=False):
        errorMessage = 'Specify either order Id in the exchange or local Id sent with the order'
        if not futures:
            if orderId is not None:
                return self.client.get_order(symbol, orderId=orderId, timestamp=time.time())
            elif localOrderId is not None:
                return self.client.get_order(symbol, origClientOrderId=localOrderId, timestamp=time.time())
            else:
                raise ValueError(errorMessage)
        else:
            if orderId is not None:
                return self.futuresClient.get_order(symbol, orderId=orderId).toDict()
            elif localOrderId is not None:
                return self.futuresClient.get_order(symbol, origClientOrderId=localOrderId).toDict()
            else:
                raise ValueError(errorMessage)

    def getTradingFees(self):
        try:
            return self.client.trade_fee()
        except Exception:
            return None

    def getSymbolTickerPrice(self, symbol, futures=False):
        if futures:
            return self.futuresClient.get_symbol_price_ticker(symbol=symbol)[0].price
        else:
            return float(self.client.ticker_price(symbol)['price'])

    def getSymbolKlines(self, symbol, interval, startTime=None, endTime=None, limit=None, futures=False, blvtnav=False,
                        convertDateTime=False, doClean=False, toCleanDataframe=False):
        if interval not in BinanceExchange.timeIntervals:
            raise ValueError('Time interval is not valid.')

        if futures:
            data = self._getFuturesSymbolKlines(blvtnav, endTime, interval, limit, startTime, symbol)
        else:
            data = self._getSpotSymbolKlines(endTime, interval, limit, startTime, symbol)

        if convertDateTime or toCleanDataframe:
            BinanceHelpers.klinesConvertDate(data)

        if doClean or toCleanDataframe:
            finalDataArray = BinanceHelpers.getKlinesDesiredOnlyCols(data)

            if toCleanDataframe:
                return BinanceHelpers.klinesConvertToPandas(finalDataArray)
            return finalDataArray
        else:
            return data

    def _getSpotSymbolKlines(self, endTime, interval, limit, startTime, symbol):
        data = self.client.klines(symbol, interval, startTime=startTime, endTime=endTime, limit=limit)
        for datum in data:
            for idx in range(len(datum)):
                if idx in BinanceExchange.timeIndexesInCandleData:
                    continue
                datum[idx] = float(datum[idx])
        return data

    def _getFuturesSymbolKlines(self, blvtnav, endTime, interval, limit, startTime, symbol):
        data = []
        if blvtnav:
            candles = self.futuresClient.get_blvt_nav_candlestick_data(symbol=symbol, interval=interval,
                                                                       startTime=startTime, endTime=endTime,
                                                                       limit=limit)
        else:
            candles = self.futuresClient.get_candlestick_data(symbol=symbol, interval=interval, startTime=startTime,
                                                              endTime=endTime, limit=limit)
        for candle in candles:
            data.append(candle.toArray())
        return data

    def getExchangeTime(self, futures=False):
        try:
            if not futures:
                return self.client.time()['serverTime']
            else:
                return self.futuresClient.get_servertime()
        except Exception:
            return None

    def getSymbol24hTicker(self, symbol):
        try:
            return self.client.ticker_24hr(symbol)
        except Exception:
            return None

    def testFuturesOrder(self, futuresOrderData):
        if not BinanceHelpers.isFuturesOrderDataValid(futuresOrderData):
            raise ValueError('Incomplete data provided.')
        return futuresOrderData

    def makeFuturesOrder(self, futuresOrderData):
        params = BinanceHelpers.getFuturesOrderAsDict(futuresOrderData)

        response = self.futuresClient.post_order(**params)
        return response.toDict()

    def makeBatchFuturesOrder(self, futuresOrderDatas):
        batchOrders = self._makeBatchOrderData(futuresOrderDatas)

        orderResults = self.futuresClient.post_batch_order(batchOrders)

        return [order.toDict() for order in orderResults]

    def _makeBatchOrderData(self, futuresOrderDatas):
        batchOrders = []
        for order in futuresOrderDatas:
            orderAsDict = BinanceHelpers.getFuturesOrderAsDict(order, allStr=True)
            orderAsDict['type'] = orderAsDict.pop('ordertype')

            orderJSON = json.dumps(orderAsDict)

            batchOrders.append(orderJSON)
        return batchOrders

    def cancellAllSymbolFuturesOrdersWithCountDown(self, symbol, countdownTime):
        return self.futuresClient.auto_cancel_all_orders(symbol, countdownTime)

    def changeInitialLeverage(self, symbol, leverage):
        return self.futuresClient.change_initial_leverage(symbol=symbol, leverage=leverage).toDict()

    def changeMarginType(self, symbol, marginType, params=None):
        if marginType not in ['ISOLATED', 'CROSSED']:
            raise ValueError('Margin type specified is not acceptable')

        return self.futuresClient.change_margin_type(symbol=symbol, marginType=marginType)

    def changePositionMargin(self, symbol, amount, marginType=None):
        if marginType not in ['ISOLATED', 'CROSSED']:
            raise ValueError('marginType was not correctly specified, should be either ISOLATED or CROSSED')

        return self.futuresClient.change_margin_type(symbol, marginType)

    def getPosition(self):
        return self.futuresClient.get_position()

    def spotBestBidAsks(self, symbol=None):
        return self.client.book_ticker(symbol=symbol)

    def getSymbolOrderBook(self, symbol, limit=None, futures=False):
        if not futures:
            if limit is None:
                return self.client.depth(symbol)
            else:
                return self.client.depth(symbol, limit=limit)
        else:
            if limit is None:
                return self.futuresClient.get_order_book(symbol=symbol)
            else:
                return self.futuresClient.get_order_book(symbol=symbol, limit=limit)

    def getSymbolRecentTrades(self, symbol, limit=None, futures=False):
        if limit is not None:
            if limit > 1000:
                limit = 1000
            elif limit < 1:
                limit = 1
        if not futures:
            if limit is None:
                return self.client.trades(symbol)
            else:
                return self.client.trades(symbol, limit=limit)
        else:
            if limit is None:
                return self.futuresClient.get_recent_trades_list(symbol=symbol)
            else:
                return self.futuresClient.get_recent_trades_list(symbol=symbol, limit=limit)

    def getPositionInfo(self, symbol=None):
        return self.futuresClient.get_position_v2(symbol)

    def getSymbolMinTrade(self, symbol, futures=False):
        tickerPrice = self.getSymbolTickerPrice(symbol, futures=futures)

        if futures:
            exchangeInfo = self.futuresClient.get_exchange_information()

            for sym in exchangeInfo.symbols:
                if sym.symbol == symbol:
                    symbolFilters = sym.filters
                    return BinanceHelpers.extractSymbolInfoFromFilters(symbolFilters, tickerPrice)
            return None
        else:
            exchangeInfo = self.client.exchange_info()

            for sym in exchangeInfo['symbols']:
                if sym['symbol'] == symbol:
                    symbolFilters = sym['filters']
                    return BinanceHelpers.extractSymbolInfoFromFilters(symbolFilters, tickerPrice)
            return None
