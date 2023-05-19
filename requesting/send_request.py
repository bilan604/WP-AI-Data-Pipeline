import requests
import json
import asyncio
import requests
import json
import base64
import requests

import tracemalloc
tracemalloc.start()



async def post_request(page_data):

    domain = "wordpress-923757-3513525.cloudwaysapps.com"
    username = "affiliat"
    password = "UZn4x67bg9C"

    user_pass = username + ":" + password
    print(user_pass)
    Authorization_Basic = base64.b64encode(user_pass.encode('utf-8')) 

    login_url = f'https://{domain}/wp-login.php'
    login_data = {
        'log': username,
        'pwd': password,
        'wp-submit': 'Log In',
        'testcookie': '1'
    }

    session = requests.Session()
    response = session.post(login_url, data=login_data)
    if response.status_code == 200:
        print('Authentication successful')
    else:
        print('Authentication failed')
        return
    
    new_post_url = f'https://{domain}/wp-json/wp/v2/posts'
    new_post_data = {
      "title": page_data["title"],
      "intro": page_data["intro"],
      "content": page_data["statistics_in_groups"],
      "conclusion": page_data["conclusion"],
      "status": "draft",
    }
    new_post_data = {
        "contentType": "application/json",
        "payload": new_post_data,
        "headers": {
           "Authorization": "Basic " + str(Authorization_Basic)
        }
    }

    response = session.post(new_post_url, json=new_post_data)
    if response.status_code == 201:
        print('Post created successfully')
    else:
        print('Failed to create post')
        print(response.text)
    return 

