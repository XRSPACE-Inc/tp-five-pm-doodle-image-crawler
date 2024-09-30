import os
import re
import time

import keywords
import pandas as pd
import requests
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

    pages, _ = get_search_resp_results()
    for page in range(1, pages+1):
        _, img_url_list = get_search_resp_results(page)
        for dl_url in img_url_list:
            check_exist_list = get_check_exist_list(archive_path)
            if dl_url in check_exist_list:
                print(f'Url exist: {dl_url}')
            if not dl_url in check_exist_list:
                print(f'Url insert: {dl_url}')
                get_dl_img(keyword, source, dl_url, time_sleep, archive_path, archive_columns, source_path)
            print('-'*3)
        print('>'*6)
        time.sleep(time_sleep)

def get_search_resp_results(page=1):
    search_url = f'https://www.freepik.com/api/regular/search?locale=en&term=chibi&page={page}'
    headers = get_headers()
    resp = requests.get(search_url, headers=headers)
    resp_results = resp.json()
    pages = resp_results['pagination']['lastPage']
    img_url_list = [i['preview']['url'] for i in resp_results['items']]
    return pages, img_url_list

def get_dl_img(keyword, source, dl_url, time_sleep, archive_path, archive_columns, source_path):
    date = get_today()
    index = get_index(archive_path)
    file_name = f'{source}_{index}.jpg'
    file_name_path = f'{source_path}/{file_name}'

    resp = requests.get(dl_url, headers=get_headers())        
    with open(file_name_path, 'wb') as f:
        f.write(resp.content)

    info_dict = {key: locals()[key] for key in archive_columns}
    print(info_dict)
    df = pd.DataFrame(info_dict, index=[0])
    df.to_csv(archive_path, mode='a', index=False, header=False)
    time.sleep(time_sleep)    

def get_headers():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }
    return headers

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
    keyword_list = ['chibi', 'ちびキャラ', 'ミニキャラ']
    for keyword in keyword_list:
        crawler_results(web, category, keyword, time_sleep=3)
