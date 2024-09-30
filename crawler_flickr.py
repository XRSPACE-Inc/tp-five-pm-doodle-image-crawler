import os
import re
import time

import keywords
import pandas as pd
import requests
from flickrapi import FlickrAPI
from utils_tool import (get_archive_columns, get_archive_path, get_current_dir,
                        get_folder_path, get_today, timer)

web_name = 'flickr'
domain_url = 'https://api.flickr.com'

root_path = './data'
download_folder = 'HumanFace'
download_path = f'{root_path}/{download_folder}'

file_path_name = f'{download_folder}_{web_name}'
file_path = f'{download_path}/archive_{file_path_name}.csv'

@timer
def crawler_results(web, category, keyword, time_sleep):
    current_dir = get_current_dir()
    source = f'{category}_{web}'
    root_path = get_folder_path(current_dir, 'data')
    category_path = get_folder_path(root_path, category)
    source_path = get_folder_path(category_path, source)
    archive_columns = get_archive_columns()
    archive_path = get_archive_path(category_path, archive_columns, source)

    pages, _ = get_search_resp_results(keyword)    
    for page in range(1, pages+1):
        try:
            _, dl_url_list = get_search_resp_results(keyword=keyword, page=page)
        except:
            continue
        for dl_url in dl_url_list:
            check_exist_list = get_check_exist_list(archive_path)
            if dl_url in check_exist_list:
                print(f'Url exist: {dl_url}')
            if not dl_url in check_exist_list:
                print(f'Url insert: {dl_url}')
                get_dl_img(keyword, source, dl_url, time_sleep, archive_path, archive_columns, source_path)
            print('-'*3)
        time.sleep(time_sleep)
        print('>'*6)
    print('-'*3)


def get_search_url(keyword, page=1):
    resp = requests.get(domain_url)
    resp_results = resp.text

    find_text_start = 'root.YUI_config.flickr.api.site_key = '
    find_text_end = ';\nroot.YUI_config.flickr.api.site_key_fetched'
    start = resp_results.find(find_text_start)
    end = resp_results.find(find_text_end)

    find_results = resp_results[start:end]
    api_key = re.sub(f'{find_text_start}|"', '', find_results)
    search_url = f'https://api.flickr.com/services/rest?sort=relevance&extrasm=media,owner_name,path_alias,realname,url_l&page={page}&text={keyword}&method=flickr.photos.search&api_key={api_key}&format=json'
    return search_url


def get_search_resp_results(keyword, page=1):
    key = '5ec5b57e56cca1a9263df1bce549c631'
    secret = '3a3ea92e096d78ca'

    flickr = FlickrAPI(key, secret, format='parsed-json')
    extras = 'media,owner_name,path_alias,realname,url_l'
    data = flickr.photos.search(
        text=keyword, # Search term
        page=page,
        per_page=500, # Number of results per page
        license='4,5,6,7,8,9,10',  # Attribution Licenses
        extras=extras, 
        privacy_filter=1,  # public photos
        safe_search=1  # is safe
    )
    pages = data['photos']['pages']
    domain_dl_url = 'https://live.staticflickr.com/'
    dl_url_list = [f'{domain_dl_url}/{i["server"]}/{i["server"]}/{i["id"]}_{i["secret"]}_b.jpg' for i in data['photos']['photo']]
    return pages, dl_url_list


def get_dl_img(keyword, source, dl_url, time_sleep, archive_path, archive_columns, source_path):
    date = get_today()
    index = get_index(archive_path)
    file_name = f'{source}_{index}.jpg'
    file_name_path = f'{source_path}/{file_name}'

    resp = requests.get(dl_url)
    with open(file_name_path, 'wb') as f:
        f.write(resp.content)

    info_dict = {key: locals()[key] for key in archive_columns}
    print(info_dict)
    df = pd.DataFrame(info_dict, index=[0])
    df.to_csv(archive_path, mode='a', index=False, header=False)


def get_check_exist_list(archive_path):
    check_rows = []
    if os.path.isfile(archive_path):
        df = pd.read_csv(archive_path)
        check_rows = df.iloc[:, -1].to_list()
    return check_rows


def get_index(archive_path):
    df = pd.read_csv(archive_path, dtype={'index': str})
    latest_index = 0 if df.empty else df['index'].max()  # Convert to number to find maximum value
    # latest_index = 0 if df.empty else df['index'].iloc[-1] # Find last value        
    return str(int(latest_index)+1).zfill(6)

if __name__ == '__main__':
    web = re.sub(r'crawler_|.py', '', os.path.basename(__file__))
    category = 'Doodle'

    keyword_list = getattr(keywords, f'{category}_keyword_list')

    for keyword in keyword_list:
        crawler_results(web, category, keyword, time_sleep=0)