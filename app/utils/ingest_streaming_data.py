import os
import base64
import asyncio
import websockets
import json
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGO_CLOUD_URI = os.getenv('MONGO_CLOUD_URI')
DATABASE = os.getenv('DATABASE')
COLLECTION = os.getenv('COLLECTION')


def generate_websocket_key():
    return base64.b64encode(os.urandom(16)).decode('utf-8')


async def get_forex_data():
    tradingview_uri = "wss://data.tradingview.com/socket.io/websocket?from=chart%2F&date=2024_06_06-12_09&type=chart"
    tradingview_headers = {
        #'Pragma': 'no-cache',
        'Origin': 'https://www.tradingview.com',
        #'Accept-Language': 'en-US,en;q=0.9,en-IN;q=0.8',
        #'Sec-WebSocket-Key': generate_websocket_key(),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
        'Upgrade': 'websocket',
        #'Cache-Control': 'no-cache',
        #'Connection': 'Upgrade',
        #'Sec-WebSocket-Version': '13',
        #'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
    }


    dailyfx_uri = 'wss://widgetdata.tradingview.com/socket.io/websocket?from=embed-widget%2Fmini-symbol-overview%2Fdailyfx%2F&date=2024_06_10-13_48&page-uri=www.dailyfx.com%2Feur-usd&ancestor-origin=www.dailyfx.com HTTP/1.1'
    dailyfx_headers = {
        
'Host': 'widgetdata.tradingview.com',
'Connection': 'Upgrade',
'Pragma': 'no-cache',
'Cache-Control': 'no-cache',
'Upgrade': 'websocket',
'Origin': 'https://www.tradingview-widget.com',
'Sec-WebSocket-Version': '13',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
'Accept-Encoding': 'gzip, deflate, br, zstd',
'Accept-Language': 'en-US,en;q=0.9',
'Sec-GPC': '1',
'Sec-WebSocket-Key': 'wAfp3C6x+TBAV2tHwBUW5Q==',
'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',


    }
    # MongoDB connection setup
    client = MongoClient(MONGO_CLOUD_URI)
    db = client[DATABASE]
    prices = db[COLLECTION]

    async with websockets.connect(dailyfx_uri, extra_headers=dailyfx_headers) as websocket:
        while True:
            message = await websocket.recv()
            print('Message\n',message)
            # You can process the message here to find the current forex data
            # For example:
            try:
                data = {'message':message}
                # Add a timestamp to the data
                data['timestamp'] = datetime.utcnow()
                # Save the data to MongoDB
                #prices.insert_one(data)
                print(f"\nSaved data: {data}")
            except json.JSONDecodeError:
                print(f"Failed to decode message: {message}")

# Start the asyncio event loop and call the function
asyncio.get_event_loop().run_until_complete(get_forex_data())