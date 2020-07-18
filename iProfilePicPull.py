#!/usr/bin/env python
# coding: utf-8

# In[66]:


import requests
import os
from concurrent.futures import ThreadPoolExecutor

def read_json(source):
    resp = requests.get(source)
    if resp.status_code == 200:
        return resp.json()


def get_urls(page_data):
    picture_url = page_data['graphql']['user']['profile_pic_url_hd']
    return picture_url

def download(url):
    filename = url.split("?")[0].split("/")[-1]
    image = requests.get(url).content
    with open("iPull Profile Pic/" + filename + ".jpg", "wb") as img_file:
        img_file.write(image)

data = read_json("https://www.instagram.com/k7.dat/?__a=1")
urls = get_urls(data)
if not os.path.isdir("iPull Profile Pic"):
    os.mkdir("iPull Profile Pic")
download(urls)


# In[ ]:




