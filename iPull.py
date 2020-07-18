import requests
import os
from concurrent.futures import ThreadPoolExecutor


def read_json(source):
    resp = requests.get(source)
    if resp.status_code == 200:
        return resp.json()


def get_urls(page_data):
    img_urls: list = []
    pictures = page_data["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
    for picture in pictures:
        if picture["node"]["__typename"] == "GraphImage":
            url = picture["node"]["display_url"]
            img_urls.append(url)
    return img_urls


def download(url):
    filename = url.split("?")[0].split("/")[-1]
    image = requests.get(url).content
    with open("iPull/" + filename + ".jpg", "wb") as img_file:
        img_file.write(image)


def i_pull(img_urls):
    with ThreadPoolExecutor() as executor:
        result = executor.map(download, img_urls)


data = read_json("https://www.instagram.com/computersciencelife/?__a=1")
urls = get_urls(data)
if not os.path.isdir("iPull"):
    os.mkdir("iPull")
i_pull(urls)
