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
    
    search_resp_results = get_search_resp_results(keyword=keyword)
    results = search_resp_results['results']
    for search_info in results:
        dl_url = search_info['images']['orig']['url']
        check_exist_list = get_check_exist_list(archive_path)
        if dl_url in check_exist_list:
            print(f'Url exist: {dl_url}')
        if not dl_url in check_exist_list:
            print(f'Url insert: {dl_url}')
            get_dl_img(keyword, source, dl_url, time_sleep, archive_path, archive_columns, source_path)
        print('-'*3)
    print('>'*6)
    time.sleep(time_sleep)

def get_search_resp_results(keyword):
    url = "https://www.pinterest.com/resource/BaseSearchResource/get/"
    page_size = 250
    params = {
        "source_url": "/search/pins",
        # "data": '{"options":{"applied_filters":null,"appliedProductFilters":"---","article":null,"auto_correction_disabled":false,"corpus":null,"customized_rerank_type":null,"domains":null,"filters":null,"page_size":null,"price_max":null,"price_min":null,"query_pin_sigs":null,"query":"rubicon mech","redux_normalize_feed":true,"rs":"typed","scope":"pins","selected_one_bar_modules":null,"source_id":null,"top_pin_id":""},"context":{}}',
        "data": f'''
            {{ 
                "options":
                    {{"appliedProductFilters":"---","auto_correction_disabled":false,
                    "corpus":null,"customized_rerank_type":null,"page_size":{page_size},
                    "query_pin_sigs":null,"query":"{keyword}","redux_normalize_feed":true,"rs":"typed",
                    "scope":"pins","selected_one_bar_modules":null,"source_id":null,"top_pin_id":""}},
                "context":{{}}
            }}'''
        # "_": "1720512445927"
    }
    resp = requests.get(url, params=params)
    resp_results = resp.json()
    return resp_results['resource_response']['data']
    
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
    latest_index = 0 if df.empty else df['index'].max() # Convert to number to find maximum value
    # latest_index = 0 if df.empty else df['index'].iloc[-1] # Find last value        
    return str(int(latest_index)+1).zfill(6)

if __name__ == '__main__':
    web = re.sub(r'crawler_|.py', '', os.path.basename(__file__))
    category = 'Doodle'

    keyword_list = getattr(keywords, f'{category}_keyword_list')

    for keyword in keyword_list:
        crawler_results(web, category, keyword, time_sleep=6)
