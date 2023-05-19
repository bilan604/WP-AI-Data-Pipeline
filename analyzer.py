import os
import re
import time
import json
import openai
import asyncio
from parsing import *





row_numbers = {}
relevent_data_by_row = {}
sentences = {}


async def get_openai_result(prompt):

    if type(prompt) != str:
        return
    if len(prompt) == 0:
        return "Empty Query Recieved"

    response = openai.Completion.create(model="text-davinci-003",
                                        prompt=prompt,
                                        max_tokens=1000)
    return response.choices[0].text


async def get_content_task(keywords_string, page_contents):
    print("REACHED PROMPT")
    
    # For all pages for all keywords for a row
    parsed_responses = []
    total_length = 0
    curr = []
    for content in page_contents:
        if sum(list(map(len, parsed_responses))) > 4000:
            break
        if total_length + len(content) >= 4000:
            page_contents_string = "\n".join(curr)

            prompt = f"The following text was extracted from a link from a Google search for the keywords \"{keywords_string}\". "
            prompt += f"Please extract and present as much empirical statistical information related to the keywords from the following text as possible:\n"
            prompt += "\"\"\"\n" + page_contents_string + "\n\"\"\"\n"
            prompt += "Format your response as a paragraph.\n"

            get_openai_result_task = asyncio.create_task(get_openai_result(prompt))
            response = await get_openai_result_task

            parsed_responses += [response]

            curr = []
            total_length = 0
        else:
            curr.append(content)
            total_length += len(content)
    
    return parsed_responses

async def generate_page_data(topic, content):
    ######### Override because AI is not remembering context very well
    use_content = content[:min(2800, len(content))]

    prompt1 = "The year is 2023 and I will need help with writting a blog about\"" + topic + "\". Here is the information that I have collected for the blog:\n"
    prompt1 += "\"\"\"\n"
    prompt1 += use_content + "\n"
    prompt1 += "\"\"\"\n"


    prompt1 += "From the information about " + topic + " generate the \"title\", \"intro\", and \"conclusion\" sections for the 2023 blog post about " + topic + ".\n"
    prompt1 += "Return your response as a Python dictionary with the keys \"title\", \"intro\",  and \"conclusion\".\n"

    task1 = asyncio.create_task(get_openai_result(prompt1))
    response1 = await task1
    # Consider saving responses here

    try:
        page_post_data = json.loads(response1)
        page_post_data["content"] = content
        return page_post_data
        
    except:
        print("Crash converting to json object")
        crash_data = {}
        crash_data["title"] = topic
        crash_data["content"] = content
        return crash_data


# cache the keywords for the row
def parse_saved_data(relevant_data_by_row, row_numbers, sentences):
    # used for abouts now
    row_keywords = {}
    page_data = {}
    for token in row_numbers:
        for aspect in row_numbers[token]:
            row = row_numbers[token][aspect]
            if row not in page_data:
                page_data[row] = []

            if row not in row_keywords:
                row_keywords[row] = aspect

            for id in relevant_data_by_row[row][token]:
                page_data[row] += [sentences[id]]
    return page_data, row_keywords


async def get_GPT_statistics_task(credentials={}):
    
    # for all keywords of all rows which have been loaded to the relevant_data_by_row, row_numbers, and sentences .json files
    data_container = load_data()
    global relevant_data_by_row, sentences, row_numbers
    relevant_data_by_row, row_numbers, sentences = data_container["relevant_data_by_row"], data_container["row_numbers"], data_container["sentences"]

    
    page_data, row_keywords = parse_saved_data(relevant_data_by_row, row_numbers, sentences)

    for row in page_data:
        if row not in row_keywords:
            print("row_keywords does not contain row", row)
            continue
        if row not in page_data:
            print("row_keywords does not contain row", row)
            continue
        if not page_data[row] or not row_keywords[row]:
            print("No data yet")
            continue

        topic = row_keywords[row]
        page_data_raw = page_data[row]
        # Filter webscrapped data with AI        
        get_parsed_responses = asyncio.create_task(get_content_task(topic, page_data_raw))
        parsed_responses = await get_parsed_responses
        # The AI filtered content
        content = get_content(parsed_responses)
        # Create AI generated blog post request data and save
        get_page_data = asyncio.create_task(generate_page_data(topic, content))
        page_post_data = await get_page_data
        
        with open("page_data.txt", "a") as f:
            try:
                # This may crash, since its an AI generated response
                data = json.dumps(page_post_data)

                f.write(str(row) + "," + data + "\n")

            except:
                print("Crash on saving data to page_data.txt")
    return


