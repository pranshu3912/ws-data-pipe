'''Data processing module for streaming prices.'''
import json
import re
import logging

import asyncio
import aiofiles


FILE_PATH = "output.txt"
logging.basicConfig(
    filename="data_process_log.txt", level=logging.DEBUG, datefmt="%(asctime)s"
)
# todo: instead of saving data to files, start working on sending it to other modules.

async def filter_stream_data(data):
    '''
    Filters streaming data to keep only the messages which are required.'''
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


async def get_message():
    '''
    Opens a message instance from messages saved to a file.
    Will not be used in further versions as data will be streamed through pipelines.'''
    async with aiofiles.open(FILE_PATH) as file:
        async for line in file:
            yield line


async def get_ohlcv(data):
    '''
    Extracts timestamp, open, high, low, close and volume from a filtered message.'''
    data = re.match(r"~m~(\d+)~m~(.*)", data).group(2).strip()
    if not data:
        print('no match')
        return None
    try:
        data = json.loads(data)
        prices = data.get("p", [None, {}])[1].get("s1", {}).get("s", [{}])[0].get("v", [])
        if prices:
            return prices
    except json.decoder.JSONDecodeError as error:
        print("Invalid JSON data:", error)
    except Exception as error:
        print(error)
    return None


async def store_processed_data():
    '''
    Function to oversee processing of obtained data.'''
    line_count = 0
    async for raw_data in get_message():
        # if line_count>=10:
        #     break

        if raw_data:
            line_count += 1
            filtered_data = await filter_stream_data(raw_data)
            if not filtered_data:
                print(f"didn't filter line {line_count}")
                continue
            processed_data = await get_ohlcv(filtered_data)
            if processed_data:
                logging.info(processed_data)
                print(processed_data)
            else:
                print('did not work on line', line_count)
        else:
            print("raw data not fetched at line ", line_count)
            break


if __name__ == '__main__':
    asyncio.run(store_processed_data())
