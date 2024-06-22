from websocket import create_connection
from typing import Dict, Optional
import json
import random
import string
import re


symbol = "EURUSD"
silent = False
output = "output.txt"
exitoninput = False


def filter_raw_message(text):
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
        "Upgrade": "websocket",
    }
)


async def filter_stream_data(data):
    try:
        match = re.match(r"~m~(\d+)~m~(.*)", data)
        if match:
            length = int(match.group(1))
            message_str = match.group(2).strip()
            if message_str:
                message = json.loads(message_str)
                if 80 <= length < 200 and message.get("m") != "critical_error":
                    return data
        return None
    except json.JSONDecodeError as error:
        print("Invalid JSON data:", error)
        return None
    except Exception as error:
        print("Some error occurred while parsing stream data", error)
        return None

class IngestionPipe:
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

    def generateSession(self):
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(stringLength))
        return "qs_" + random_string

    def generateChartSession(self):
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(stringLength))
        return "cs_" + random_string

    def prependHeader(self, st):
        return "~m~" + str(len(st)) + "~m~" + st

    def constructMessage(self, func, paramList):
        # json_mylist = json.dumps(mylist, separators=(',', ':'))
        return json.dumps({"m": func, "p": paramList}, separators=(",", ":"))

    def createMessage(self, func, paramList):
        return self.prependHeader(self.constructMessage(func, paramList))

    def sendRawMessage(self, ws, message):
        ws.send(self.prependHeader(message))

    def sendMessage(self, ws, func, args):
        ws.send(self.createMessage(func, args))

    def start_ws_connection(self):
        self.ws = create_connection(self.uri)
        self.session = self.generateSession()
        if not self.silent:
            print("session generated {}".format(self.session))

        self.chart_session = self.generateChartSession()
        if not self.silent:
            print("session generated {}".format(self.session))

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
            [self.session, symbol, {"flags": ["force_permission"]}],
        )
        self.sendMessage(self.ws, "quote_fast_symbols", [self.session, symbol])
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
        if not silent:
            self.sendMessage(
                self.ws,
                "create_series",
                [self.chart_session, "s1", "s1", "symbol_1", "1", 5000],
            )

    def run(self):
        self.start_ws_connection()
        a = ""
        while True:
            try:
                if self.ws.connected:
                    result = self.ws.recv()
                    if not silent:
                        print(result)
                    if silent:
                        if not re.search(r'"lp":(.*?),', result) is None:
                            print(re.search(r'"lp":(.*?),', result).group(1))
                            if self.exitoninput:
                                exit(0)
                    a = a + result + "\n"
                    if output:
                        with open(output, "a") as ww:
                            ww.write(result)
                            ww.write("\n")
                            ww.close()
                else:
                    print(
                        "\nConnection closed, re-establishing websocket connection now."
                    )
                    self.start_ws_connection()
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
            "Upgrade": "websocket",
        }
    )

    pipe = IngestionPipe(
        "EURUSD",
        "output.txt",
        "wss://data.tradingview.com/socket.io/websocket",
        headers=headers,
    )
    pipe.run()
