import json
import os
import re
import time

import keywords
import pandas as pd
import requests
from bs4 import BeautifulSoup
from utils_tool import (get_archive_columns, get_archive_path, get_current_dir,
                        get_folder_path, get_today, timer)


@timer
def crawler_results(web, category, keyword, time_sleep):
    current_dir = get_current_dir()
    source = f'{category}_{web}'
    root_path = get_folder_path(current_dir, 'data')
    category_path = get_folder_path(root_path, category)
    source_path = get_folder_path(category_path, source)
    archive_columns = get_archive_columns()
    archive_path = get_archive_path(category_path, archive_columns, source)

    url = f'https://pikbest.com/so/{keyword}.html'
    pages = int(get_pages(url))

    for p in range(1, pages+1):
        elements = get_search_resp_results(url, p)
        if elements:
            for elem in elements:
                content = json.loads(elem.get_text())
                dl_url = content['contentUrl']
                check_exist_list = get_check_exist_list(archive_path)
                if dl_url in check_exist_list:
                    print(f'Url exist: {dl_url}')
                if not dl_url in check_exist_list:
                    print(f'Url insert: {dl_url}')
                    get_dl_img(keyword, source, dl_url, time_sleep, archive_path, archive_columns, source_path)
                print('-'*3)
        time.sleep(time_sleep)    
        print('>'*6)

def get_search_resp_results(url, p):
    soup = get_soup(f'{url}?p={p}') 
    return soup.select('.list-item >script')
    
def get_pages(url):
    soup_pages = get_soup(url) 
    return soup_pages.select('.numtotal')[0].get_text()

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

def get_soup(url, cookies=None):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',}
    resp = requests.get(url, headers=headers)
    return BeautifulSoup(resp.text, 'lxml')

def get_check_exist_list(archive_path):
    check_rows = []
    if os.path.isfile(archive_path):
        df = pd.read_csv(archive_path)
        check_rows = df.iloc[:, -1].to_list()
    return check_rows

def get_index(archive_path):
    df = pd.read_csv(archive_path, dtype={'index': str})
    latest_index = 0 if df.empty else df['index'].max() # Convert to number to find maximum value
    # latest_index = 0 if df.empty else df['index'].iloc[-1] # Find last value        
    return str(int(latest_index)+1).zfill(6)

if __name__ == '__main__':
    web = re.sub(r'crawler_|.py', '', os.path.basename(__file__))
    category = 'Doodle'

    keyword_list = getattr(keywords, f'{category}_keyword_list')

    for keyword in keyword_list:
        crawler_results(web, category, keyword, time_sleep=6)