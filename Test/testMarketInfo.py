import json
import logging

import pytest

from TradeGates.TradeGate import TradeGate

loglevel = logging.INFO
logging.basicConfig(level=loglevel)
log = logging.getLogger(__name__)


@pytest.fixture
def getGates():
    gates = []
    with open('./config.json') as f:
        config = json.load(f)

    for key in config.keys():
        gates.append(TradeGate(config[key], sandbox=True))

    return gates


@pytest.mark.skip(reason="Only works with main network")
def testTradingFees(getGates):
    for gate in getGates:
        tradingFees = gate.getTradingFees()
        # print('\nTrading fees from {} exchange: {}'.format(gate.exchangeName, tradingFees))

        assert tradingFees is not None, 'Problem in fetching trading fees from {} exchange.'.format(gate.exchangeName)


def testRecentTrades(getGates):
    for gate in getGates:
        symbolRecentPrice = gate.getSymbolRecentTrades('BTCUSDT')
        # print('\nBTCUSDT recent trades from {} exchange: {}'.format(gate.exchangeName, symbolRecentPrice[0]))

        assert symbolRecentPrice is not None, 'Problem in fetching symbol latest price from {} exchange.'.format(
            gate.exchangeName)

        futuresSymbolRecentPrice = gate.getSymbolRecentTrades('BTCUSDT', futures=True)
        # print(
        #     '\nBTCUSDT futures recent trades from {} exchange: {}'.format(gate.exchangeName,
        #                                                                   futuresSymbolRecentPrice[0]))

        assert futuresSymbolRecentPrice is not None, 'Problem in fetching symbol latest price from {} exchange.'.format(
            gate.exchangeName)


def testTickerPrice(getGates):
    for gate in getGates:
        symbolTickerPrice = gate.getSymbolTickerPrice('BTCUSDT')
        # print('\nBTCUSDT ticker Price from {} exchange: {}'.format(gate.exchangeName, symbolTickerPrice))

        assert symbolTickerPrice is not None, 'Problem in fetching symbol ticker price from {} exchange.'.format(
            gate.exchangeName)

        symbolTickerPrice = gate.getSymbolTickerPrice('BTCUSDT', futures=True)
        # print('\nBTCUSDT ticker price from futures market of {} exchange: {}'.format(gate.exchangeName,
        # symbolTickerPrice))

        assert symbolTickerPrice is not None, 'Problem in fetching symbol ticker price from {} exchange.'.format(
            gate.exchangeName)


def testKlines(getGates):
    for gate in getGates:
        # print('\nBTCUSDT candles: {}'.format(gate.getSymbolKlines('BTCUSDT', '1m', limit=10)))
        spotData = gate.getSymbolKlines('BTCUSDT', '15m', limit=10, futures=False, toCleanDataframe=True)
        assert spotData is not None, 'Problem in fetching spot market candle data from {} exchange.'.format(
            gate.exchangeName)
        assert len(spotData) == 10, 'Length of spot market candle data is incorrect from {} exchange.'.format(
            gate.exchangeName)

        futuresData = gate.getSymbolKlines('BTCUSDT', '15m', limit=10, futures=True, toCleanDataframe=True)
        assert futuresData is not None, 'Problem in fetching spot market candle data from {} exchange.'.format(
            gate.exchangeName)
        assert len(futuresData) == 10, 'Length of spot market candle data is incorrect from {} exchange.'.format(
            gate.exchangeName)

        assert futuresData.shape == (10, 7), '7 columns were excpected, but failed from {} exchange.'.format(
            gate.exchangeName)


def testExchangeTime(getGates):
    for gate in getGates:
        exchangeTime = gate.getExchangeTime()
        # print('\nExchange time from spot market of {} exchange: {}'.format(gate.exchangeName, exchangeTime))
        assert exchangeTime is not None, 'Problem in fetching exchange time from {} exchange.'.format(gate.exchangeName)

        exchangeTime = gate.getExchangeTime(futures=True)
        # print('\nExchange time from futures market of {} exchange: {}'.format(gate.exchangeName, exchangeTime))
        assert exchangeTime is not None, 'Problem in fetching exchange time from {} exchange.'.format(gate.exchangeName)
