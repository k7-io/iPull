import requests
from datetime import datetime
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

current_page = 1

headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"}

def read_json(source):
    resp = requests.get(source,headers=headers)
    if resp.status_code == 200:
        return resp.json()
    else:
        print("invalid username provided")
        sys.exit(1)


def get_urls(page_data):
    img_urls: list = []
    time_stamps: list = []
    if page_data.get("data"):
        pictures = page_data["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
    else:
        pictures = page_data["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
    for picture in pictures:
        if picture["node"]["__typename"] == "GraphImage":
            url = picture["node"]["display_url"]
            time_posted=datetime.fromtimestamp(picture['node']['taken_at_timestamp']).strftime("%d %B %Y %H %M %S")
            time_stamps.append(time_posted)
            img_urls.append(url)
        if picture["node"]["__typename"] == "GraphSidecar":
            sidecar_pictures = picture["node"]["edge_sidecar_to_children"]["edges"]
            id_count=0
            for sidecar_picture in sidecar_pictures:
                if sidecar_picture["node"]["__typename"] == "GraphImage":
                    url = sidecar_picture["node"]["display_url"]
                    time_posted=datetime.fromtimestamp(picture['node']['taken_at_timestamp']).strftime("%d %B %Y %H %M %S")
                    if time_posted in time_stamps:
                        time_stamps.append(time_posted+str(id_count))
                    else:
                        time_stamps.append(time_posted)
                    img_urls.append(url)
                    id_count+=1  
    return img_urls,time_stamps


def download(url,timestamps):
    pic_id= url.split("?")[0].split("/")[-1]
    pic_id=pic_id.split('_')[0]
    filename = str(pic_id)+' '+timestamps+'.jpg'
    image = requests.get(url).content
    with open("iPull/" + filename, "wb") as img_file:
        img_file.write(image)


def i_pull(img_urls,timestamps):
    with ThreadPoolExecutor() as executor:
        _ = executor.map(download, img_urls,timestamps)


# keep a note on the query string
def generate_next_page(u_id, end_cursor):
    next_page = 'https://www.instagram.com/graphql/query/?query_hash=15bf78a4ad24e33cbd838fdb31353ac1&variables={"id":"' +         u_id + '","first":50,"after":"' + end_cursor + '"}'
    return next_page


def extract_page_info(data):
    if data.get("data"):
        page_info = data["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]
    else:
        page_info = data["graphql"]["user"]["edge_owner_to_timeline_media"]["page_info"]
    has_next_page = page_info["has_next_page"]
    end_cursor = page_info["end_cursor"]
    return has_next_page, end_cursor


def create_dir():
    path = Path("iPull/Profile_pic")
    path.mkdir(parents=True, exist_ok=True)


def get_user_id(data):
    u_id = data["graphql"]["user"]["id"]
    return u_id


def val_profile_type(data):
    is_private = data["graphql"]["user"]["is_private"]
    return is_private


def download_profile_image(data):
    profile_image = data['graphql']['user']['profile_pic_url_hd']
    filename = datetime.fromtimestamp(data['graphql']['user']['edge_owner_to_timeline_media']['edges'][0]['node']['taken_at_timestamp']).strftime("%d %B %Y %H %M %S")+'.jpg'
    image = requests.get(profile_image).content
    with open("iPull/Profile_pic/" + filename, "wb") as img_file:
        img_file.write(image)

username = input("Enter the Username: ")
source = f"https://www.instagram.com/{username}/?__a=1"
create_dir()
data = read_json(source)
u_id = get_user_id(data)
is_private = val_profile_type(data)
download_profile_image(data)
# print(data['graphql']['user']['edge_owner_to_timeline_media'])
s=data['graphql']['user']['edge_owner_to_timeline_media']
if not is_private:
    while True:
        urls,timestamps = get_urls(data)
        print("Downloading page : {}".format(current_page))
        i_pull(urls,timestamps)
        has_next_page, end_cursor = extract_page_info(data)
        if not has_next_page:
            print("All the images have been successfully Pulled")
            break
        next_page = generate_next_page(u_id, end_cursor)
        data = read_json(next_page)
        current_page = current_page + 1
else:
    print("The provided account is not Public and hence only the profile image is pulled")

