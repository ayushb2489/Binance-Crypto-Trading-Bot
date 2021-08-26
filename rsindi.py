''' Naked RSI Indicator Trade'''

import websocket
import json
import numpy
import talib
from binance.client import Client
from binance.enums import *

#Socket stream taken from = https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md
#Base end point = wss://stream.binance.com:9443
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1h"
RSI_PERIOD = 14
OVERBOUGHT = 70
OVERSOLD = 30
TRADE_SYMBOL = 'BTCUSDT'
TRADE_QUANTITY = 0.001
# These are constant values that does not change with time


'''
making a client 
api key and api secret hidden here, varies according to user'''

client = Client (********API_KEY********* , ********API_SECRET*********)




#Sending order (return True is order successful else False)
def order (symbol, quantity, side):
    try:
        order = client.create_order (symbol = symbol, side = side, type = ORDER_TYPE_MARKET, quantity = quantity) 

    except Exception as e:
        print (e)
        return False

    return True


stream_array = []           # Container for ltp
position = False            # Open postion or not

# These methods requires a reference to the websocket object

def onOpen (ws):
    print ("Connection Opened")

def onClose (ws):
    print ("Connection Closed")

def onMessage (ws, message):
    print ("Message Received")

    # converting json message to pyhon data structure
    json_message = json.loads (message) 


    candle_closed = json_message['k']['x']
    ltp = json_message['k']['c']

    if candle_closed:
        print ("Candle closes at {}".format (ltp))

        stream_array.append (float (ltp))
        print (stream_array)

        if len(stream_array) > 15:
            # rsi works with numpy array 
            np_stream_array = numpy.array (stream_array)

            rsi = talib.RSI (np_stream_array, RSI_PERIOD)

            print ("RSI")
            print (rsi)

            last_rsi = rsi[-1]
            print ("Current RSI {}".format (last_rsi))


            # Buy and Sell Order Logic  (rsi)
            if (last_rsi > OVERBOUGHT):
                if position:
                    order_succeeded = order (TRADE_SYMBOL, SIDE_SELL, TRADE_QUANTITY)
                    
                    if order_succeeded:
                        print ("{} sold at {}".format (TRADE_SYMBOL, ltp))
                        position = False
                    else:
                        print ("Order Failed")

            if (last_rsi < OVERSOLD):
                if (not position):
                    order_succeeded = order (TRADE_SYMBOL, SIDE_BUY, TRADE_QUANTITY)

                    if (order_succeeded):
                        print ("{} bought at {}".format (TRADE_SYMBOL, ltp))
                        postion = True

                    else:
                        print ("Order Failed")

ws = websocket.WebSocketApp (SOCKET, on_open = onOpen, on_close = onClose, on_message = onMessage)

# After we connect these are callback function be called on each event

ws.run_forever()
