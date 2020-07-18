import requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

current_page = 1


def read_json(source):
    resp = requests.get(source)
    if resp.status_code == 200:
        return resp.json()


def get_urls(page_data):
    img_urls: list = []
    if page_data.get("data"):
        pictures = page_data["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
    else:
        pictures = page_data["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
    for picture in pictures:
        if picture["node"]["__typename"] == "GraphImage":
            url = picture["node"]["display_url"]
            img_urls.append(url)
    return img_urls


def download(url):
    filename = url.split("?")[0].split("/")[-1]
    image = requests.get(url).content
    with open("iPull/" + filename, "wb") as img_file:
        img_file.write(image)


def i_pull(img_urls):
    with ThreadPoolExecutor() as executor:
        _ = executor.map(download, img_urls)


# keep a note on the query string
def generate_next_page(u_id, end_cursor):
    next_page = 'https://www.instagram.com/graphql/query/?query_hash=15bf78a4ad24e33cbd838fdb31353ac1&variables={"id":"' + \
        u_id + '","first":50,"after":"' + end_cursor + '"}'
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
    filename = profile_image.split("?")[0].split("/")[-1]
    image = requests.get(profile_image).content
    with open("iPull/Profile_pic/" + filename, "wb") as img_file:
        img_file.write(image)

create_dir()
data = read_json("https://www.instagram.com/k7.dat/?__a=1")
u_id = get_user_id(data)
is_private = val_profile_type(data)
download_profile_image(data)
if not is_private:
    while True:
        urls = get_urls(data)
        print("Downloading page : {}".format(current_page))
        i_pull(urls)
        has_next_page, end_cursor = extract_page_info(data)
        if not has_next_page:
            break
        next_page = generate_next_page(u_id, end_cursor)
        data = read_json(next_page)
        current_page = current_page + 1
else:
    print("The provided account is not Public and hence only the profile image is pulled")
