import openai
import os
import asyncio
import pandas as pd
from handler import get_handle_statistics
from analyzer import get_GPT_statistics_task


def clear():
    import json
    with open("data_container/relevant_data_by_row.json", "w") as f1:
        json.dump({}, f1)
    with open("data_container/sentences.json", "w") as f2:
        json.dump({}, f2)        
    with open("data_container/row_numbers.json", "w") as f3:
        json.dump({}, f3)


async def collect_data(credentials):
    
    # Blacklisted URLs as list
    blacklisted_urls = ["www.bloomberg.com", "www.kinsta.com", "www.nasdaq.com", "www.ycharts.com"]
    
    
    df = pd.read_csv("input.csv")
    queries = {}
    columns = {colName: list(df[colName]) for colName in df.columns}

    for i in range(len(df)):
        queries[i] = {
            "keywords": columns["keywords"][i],
            "results to check": columns["results to check"][i],
            "status": columns["status"][i]
        }
    
    get_statistics = asyncio.create_task(get_handle_statistics(queries, blacklisted_urls, credentials))
    await get_statistics
    return 


async def main(webscrapping=True, clear_data=False, credentials={}):
    # Mode: webscrapping = True for collecting data
    
    if webscrapping:
        if clear_data:
            # Clear the data_container
            clear()
        
        # Webscrape data
        task = asyncio.create_task(collect_data(credentials))
        await task
    else:
        # Generate post request jsons from webscrapped data
        task = asyncio.create_task(get_GPT_statistics_task(credentials))
        await task


if __name__ == '__main__':
    os.chdir("c:/Users/bill/github/WP-AI-Data-Pipeline")

    credentials = {}
    with open(".env", "r") as f:
        lines = f.readlines()
        for row in lines:
            if not row:
                break
            if row[-1] == "\n":
                row = row[:-1]
            key, value = row.split("=")
            credentials[key] = value
    
    KEY = credentials["OPENAI_API_KEY"]
    openai.api_key = KEY

    asyncio.run(main(webscrapping=True, clear_data=True, credentials=credentials))

    #asyncio.run(main(webscrapping=False, clear_data=False))
    
