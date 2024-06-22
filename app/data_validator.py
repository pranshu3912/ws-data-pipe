import json
import re
import asyncio
import aiofiles
import logging
from ingestion.data_pipe import filter_stream_data


FILE_PATH = "output.txt"
logging.basicConfig(
    filename="data_process_log.txt", level=logging.DEBUG, datefmt="%(asctime)s"
)


async def get_message():
    async with aiofiles.open(FILE_PATH) as file:
        async for line in file:
            yield line


async def get_ohlcv(data):
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