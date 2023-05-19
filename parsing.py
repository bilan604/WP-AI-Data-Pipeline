import re
import json
import time

def save_sentences(data):
    with open("data_container/sentences.json", "w") as f:
        json.dump(data, f)

def save_row_numbers(data):
    with open("data_container/row_numbers.json", "w") as f:
        json.dump(data, f)

def save_relevant_data(data):
    with open("data_container/relevant_data_by_row.json", "w") as f:
        json.dump(data, f)

    return

def load_data():
    dd = {}
    a,b,c = None, None, None
    with open("data_container/sentences.json", "r") as f1:
        a = json.load(f1)
    with open("data_container/row_numbers.json", "r") as f2:
        b = json.load(f2)
    with open("data_container/relevant_data_by_row.json", "r") as f3:
        c = json.load(f3)
    for row in c:
        for token in c[row]:
            c[row][token] = set(c[row][token])
    
    dd["relevant_data_by_row"] = c
    dd["row_numbers"] = b
    dd["sentences"] = a

    

    return dd


def save_completed_keywords(keywords: list):
    vis = set(get_completed_keywords())
    with open("data_helper_folder/completed_keywords.txt", "r") as f:
        vis = set([line[:-1] for line in f.readlines()])
    
    with open("data_helper_folder/completed_keywords.txt", "a") as f:
        for keyword in keywords:
            if keyword not in vis:
                f.write(keyword+"\n")
    return

def get_completed_keywords():
    # Append string to file
    with open("data_helper_folder/completed_keywords.txt", "r") as f:
        return [s[:-1] for s in f.readlines() if s]


def filter_spacing(s):
    s = re.sub("\n+?", " ", s)
    s = re.sub(" +", " ", s)
    return s.strip()

def to_key(s):
    s = re.sub("\(.+?\)", "", s)
    s = s.lower()
    s = filter_spacing(s)
    return s

def listify(relevant_data_by_row):
    dd = {}
    for k in relevant_data_by_row:
        dd[k] = {}
        for kk in relevant_data_by_row[k]:
            dd[k][kk] = list(relevant_data_by_row[k][kk])
    return dd

def get_filtered_keywords(keywords):
    ans = []
    keywords = keywords.lower().split(",")
    dd = {}
    for s in keywords:
        c = s.split(" ")
        for word in c:
            if word not in dd:
                dd[word] = 0
            dd[word] += 1
    
    aspect = ""
    for word in dd:
        if dd[word] == len(keywords):
            if not aspect:
                aspect = word
            else:
                aspect += " " + word
    aspect = re.sub("[^a-zA-Z| |\(|\)]", "", aspect)
    for keyword in keywords:
        filtered_keyword = to_key(keyword)    
        filtered_keyword = " ".join([word for word in filtered_keyword.split(" ") if dd[word] < len(keywords)])
        ans.append(filtered_keyword)
    return aspect, ans

def filter_parsed_responses(lst):
    import string
    newLst = []
    for i, s in enumerate(lst):
        letters = list(s)
        while letters and not letters[-1] in string.ascii_letters:
            letters.pop()
        if letters:
            letters.reverse()
            while letters and not letters[-1] in string.ascii_letters:
                letters.pop()
            letters.reverse()
        if letters:
            newLst.append("".join(letters) + ".")
        
    lst = [s for s in newLst if len(s.split(" ")) > 3]
    return lst

def basic_filter(s):
    s = re.sub("\n", " ", s)
    s = re.sub(" +?", " ", s)
    return s

def get_content(parsed_responses):
    contents = []
    total = 0
    for s in parsed_responses:
        for sentence in s.split("."):
            if total + len(sentence) < 4000:
                contents.append(sentence)
            else:
                break
    
    content = ". ".join(contents)
    content = re.sub("\n", " ", content)
    content = re.sub(" +?", " ", content)
    return content

def parse_response1(resp1):
    resp1 = re.sub("\n", " ", resp1)
    resp1 = re.sub(" +", " ", resp1)
    resp1 = re.sub("'", "\"", resp1)
    resp1 = re.sub("{( )+?", "{", resp1)
    resp1 = re.sub("( )+?}", "}", resp1)
    s = ""
    add = False
    for letter in resp1:
        if letter == "{":
            add = True
        elif letter == "}":
            add = False
        else:
            if add:
                s += letter
    return "{"+s+"}"

