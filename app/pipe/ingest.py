'''
Code to ingest data from web sources.
'''
from typing import Dict, Optional
import json
import random
import string
import re

from websocket import create_connection


SYMBOL = "EURUSD"
SILENT = False
OUTPUT = "output.txt"
EXITONINPUT = False
# todo: figure out if all those functions are really needed or they increase complexity
# todo: change names to conform to snake case.

def filter_raw_message(text):
    '''
    Not used right now'''
    try:
        found1 = re.search('"m":"(.+?)",', text).group(1)
        found2 = re.search('"p":(.+?"}"])}', text).group(1)
        print(found1)
        print(found2)
        return found1, found2
    except AttributeError:
        print("error")


headers = json.dumps(
    {
        "Connection": "upgrade",
        "Host": "data.tradingview.com",
        "Origin": "https://data.tradingview.com",
        "Cache-Control": "no-cache",
        "Upgrade": "websocket",
        "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
        "Sec-WebSocket-Key": "2C08Ri6FwFQw2p4198F/TA==",
        "Sec-WebSocket-Version": "13",
        "User-Agent": "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56",
        "Pragma": "no-cache",
    }
)


class IngestionPipe:
    '''
    Ingestion pipeline for getting data from raw source.
    '''
    def __init__(
        self,
        symbol: str,
        output_file_path: str,
        uri: str,
        headers: Optional[Dict[str, str]],
    ) -> None:
        self.symbol = symbol
        self.uri = uri
        self.silent = False
        self.output = output_file_path
        self.exitoninput = False
        self.ws = None
        self.session = None
        self.chart_session = None
        self.headers = headers
        self.STRING_LENGTH = 12


    def generateSession(self):
        '''Generates a session for ws connection.'''
        STRING_LENGTH = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(STRING_LENGTH))
        return "qs_" + random_string
# TODO: find out the difference between a session and a chart session, and if its really necessary to make both

    def generateChartSession(self):
        '''Generates a chart session for ws connection.'''
        STRING_LENGTH = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(STRING_LENGTH))
        return "cs_" + random_string

    def prependHeader(self, st):
        '''
        Adds a header to a string'''
        # todo: figure out what this is for
        return "~m~" + str(len(st)) + "~m~" + st

    def constructMessage(self, func, param_list):
        '''
        Standard message imitation.'''
        # json_mylist = json.dumps(mylist, separators=(',', ':'))
        return json.dumps({"m": func, "p": param_list}, separators=(",", ":"))

    def createMessage(self, func, param_list):
        '''
        Creates message.'''
        return self.prependHeader(self.constructMessage(func, param_list))

    def sendRawMessage(self, ws, message):
        '''
        Sends message with headers'''
        ws.send(self.prependHeader(message))

    def sendMessage(self, ws, func, args):
        '''
        Sends a standard message.'''
        ws.send(self.createMessage(func, args))

    def start_ws_connection(self):
        '''
        Creates a ws connection to fetch data.'''
        self.ws = create_connection(self.uri)
        self.session = self.generateSession()
        if not self.silent:
            print(f"session generated {self.session}")

        self.chart_session = self.generateChartSession()
        if not self.silent:
            print(f"session generated {self.session}")

        self.sendMessage(self.ws, "set_auth_token", ["unauthorized_user_token"])
        self.sendMessage(self.ws, "chart_create_session", [self.chart_session, ""])
        self.sendMessage(self.ws, "quote_create_session", [self.session])

        self.sendMessage(
            self.ws,
            "quote_set_fields",
            [
                self.session,
                "ch",
                "chp",
                "current_session",
                "description",
                "local_description",
                "language",
                "exchange",
                "fractional",
                "is_tradable",
                "lp",
                "lp_time",
                "minmov",
                "minmove2",
                "original_name",
                "pricescale",
                "pro_name",
                "short_name",
                "type",
                "update_mode",
                "volume",
                "currency_code",
                "rchp",
                "rtc",
            ],
        )
        self.sendMessage(
            self.ws,
            "quote_add_symbols",
            [self.session, self.symbol, {"flags": ["force_permission"]}],
        )
        self.sendMessage(self.ws, "quote_fast_symbols", [self.session, self.symbol])
        self.sendMessage(
            self.ws,
            "resolve_symbol",
            [
                self.chart_session,
                "symbol_1",
                '={"symbol":"'
                + self.symbol
                + '","adjustment":"splits","session":"extended"}',
            ],
        )
        if not self.silent:
            self.sendMessage(
                self.ws,
                "create_series",
                [self.chart_session, "s1", "s1", "symbol_1", "1", 5000],
            )

    def run(self):
        '''
        Gets all the data from ws while a connection is established'''
        self.start_ws_connection()
        a = ""
        while True:
            try:
                if not self.ws.connected:
                    print(
                        "\nConnection closed, re-establishing websocket connection now."
                    )
                    self.start_ws_connection()
                    continue
                result = self.ws.recv()
                if not self.silent:
                    print(result)
                if self.silent:
                    if not re.search(r'"lp":(.*?),', result) is None:
                        print(re.search(r'"lp":(.*?),', result).group(1))
                        if self.exitoninput:
                            exit(0)
                a = a + result + "\n"
                if self.output:
                    with open(self.output, "a") as ww:
                        ww.write(result)
                        ww.write("\n")
                        ww.close()
            except Exception as e:
                print(e)
                break


# st='~m~140~m~{"m":"resolve_symbol","p":}'
# p1, p2 = filter_raw_message(st)
# sendMessage(ws, "create_study", [chart_session,"st4","st1","s1","ESD@tv-scripting-101!",{"text":"BNEhyMp2zcJFvntl+CdKjA==_DkJH8pNTUOoUT2BnMT6NHSuLIuKni9D9SDMm1UOm/vLtzAhPVypsvWlzDDenSfeyoFHLhX7G61HDlNHwqt/czTEwncKBDNi1b3fj26V54CkMKtrI21tXW7OQD/OSYxxd6SzPtFwiCVAoPbF2Y1lBIg/YE9nGDkr6jeDdPwF0d2bC+yN8lhBm03WYMOyrr6wFST+P/38BoSeZvMXI1Xfw84rnntV9+MDVxV8L19OE/0K/NBRvYpxgWMGCqH79/sHMrCsF6uOpIIgF8bEVQFGBKDSxbNa0nc+npqK5vPdHwvQuy5XuMnGIqsjR4sIMml2lJGi/XqzfU/L9Wj9xfuNNB2ty5PhxgzWiJU1Z1JTzsDsth2PyP29q8a91MQrmpZ9GwHnJdLjbzUv3vbOm9R4/u9K2lwhcBrqrLsj/VfVWMSBP","pineId":"TV_SPLITS","pineVersion":"8.0"}])


if __name__ == "__main__":
    headers = headers = json.dumps(
        {
            "Connection": "upgrade",
            "Host": "data.tradingview.com",
            "Origin": "https://data.tradingview.com",
            "Cache-Control": "no-cache",
            "Upgrade": "websocket",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Sec-WebSocket-Key": "2C08Ri6FwFQw2p4198F/TA==",
            "Sec-WebSocket-Version": "13",
            "User-Agent": "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56",
            "Pragma": "no-cache",
        }
    )

    pipe = IngestionPipe(
        "EURUSD",
        "output.txt",
        "wss://data.tradingview.com/socket.io/websocket",
        headers=headers,
    )
    pipe.run()
