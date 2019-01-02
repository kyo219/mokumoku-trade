import configparser
import datetime
import v20

config = configparser.ConfigParser()
config.read('api/oanda_conf.ini')

hostname = config['DEMO']['HOSTNAME']
port = int(config['DEMO']['PORT'])
token = config['DEMO']['TOKEN']

context = v20.Context(
            hostname,
            port,
            token=token
        )
account_id = context.account.list().get('accounts', 200)[0].id

instrument = 'USD_JPY'
candles_params = {
    'granularity': 'M5',
    'count': 60
}

def format_candle(candle):
    return {
        'datetime': str(datetime.datetime.strptime(
            candle.time.split('.')[0] + '+00:00',
            '%Y-%m-%dT%H:%M:%S%z')),
        'open': candle.mid.o,
        'high': candle.mid.h,
        'low':candle.mid.l,
        'close': candle.mid.c
    }

def format_trade(trade):
    return {
        'tradeId': trade.id,
        'instrument': trade.instrument,
        'price': trade.price,
        'openTime': trade.openTime,
        'state': trade.state,
        'initialUnits': trade.initialUnits,
        'realizedPL': trade.realizedPL,
        'unrealizedPL': trade.unrealizedPL,
        'averageClosePrice': trade.averageClosePrice,
        'closeTime': trade.closeTime
    }

def get_candles(instrument=instrument, params=candles_params, completed_only=True):
    candles = context.instrument.candles(instrument, **params).get("candles", 200)
    if completed_only:
        candles = [candle for candle in candles if candle.complete]

    return list(map(lambda candle: format_candle(candle), candles))

def market_order(units):
    stop_loss = {
        'distance': str(0.200)
    }

    params = {
        'type': 'MARKET',
        'instrument': instrument,
        'units': str(units),
        'timeInForce': 'FOK',
        'stopLossOnFill': stop_loss
    }

    response = context.order.market(account_id, **params)
    return response

def get_trades(state, count):
    params = {
        'state': state,
        'instrument': instrument,
        'count': count
    }
    trades = context.trade.list(account_id, **params).get('trades', 200)

    return list(map(lambda trade: format_trade(trade), trades))

def close_trade(trade_id):
    response = context.trade.close(account_id, str(trade_id))
    return response

def close_all_position(side):
    params = {}
    if side == 'short':
        params = {
            'shortUnits': 'ALL'
        }
    if side == 'long':
        params = {
            'longUnits': 'ALL'
        }
    response = context.position.close(
        account_id, instrument=instrument, **params
    )
    return response

def is_market_open():
    instrument = 'USD_JPY'
    candles_params = {
        'granularity': 'S5',
        'count': 1
    }
    candle = get_candles(instrument, candles_params, False)[0]

    now = datetime.datetime.now(datetime.timezone.utc)
    candle_time = datetime.datetime.strptime(
        candle['datetime'],
        '%Y-%m-%d %H:%M:%S%z'
    )

    if now - candle_time > datetime.timedelta(minutes=30):
        return False
    else:
        return True
