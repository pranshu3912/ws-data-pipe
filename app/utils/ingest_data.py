import json
import re
from datetime import datetime

import asyncio
import websockets


URI = ''

async def connect_to_ws():
    async with websockets.connect(URI) as websocket:
        while True:
            message = await websocket.recv()
            print(message)

asyncio.get_event_loop().run_until_complete(connect_to_ws)

