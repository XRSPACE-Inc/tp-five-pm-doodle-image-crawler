import os
import re
import time

import keywords
import pandas as pd
import requests
from dotenv import load_dotenv
from utils_tool import get_archive_columns
from utils_tool import get_archive_path
from utils_tool import get_current_dir
from utils_tool import get_folder_path
from utils_tool import get_today
from utils_tool import timer

load_dotenv(override=True)

@timer
def crawler_results(web, category, keyword, time_sleep):
    current_dir = get_current_dir()
    source = f'{category}_{web}'
    root_path = get_folder_path(current_dir, 'data')
    category_path = get_folder_path(root_path, category)
    source_path = get_folder_path(category_path, source)
    archive_columns = get_archive_columns()
    archive_path = get_archive_path(category_path, archive_columns, source)

    pages = 3  # The maximum number obtained using the api key is 600, and the maximum number of pages is 3.

    for page in range(1, pages+1):
        search_resp_results = get_search_resp_results(keyword=keyword, page=page)
        results = search_resp_results['hits']
        for search_info in results:
            dl_url = search_info['previewURL'].replace('_150', '_1280')
            check_exist_list = get_check_exist_list(archive_path)
            if dl_url in check_exist_list:
                print(f'Url exist: {dl_url}')
            if not dl_url in check_exist_list:
                print(f'Url insert: {dl_url}')
                get_dl_img(keyword, source, dl_url, time_sleep, archive_path, archive_columns, source_path)
            print('-'*3)
        print('>'*6)
        time.sleep(time_sleep)


def get_search_resp_results(keyword, page):
    pixabay_api_key = os.getenv('PIXABAY_API_KEY')
    per_page = 200
    search_url = f'https://pixabay.com/api/?key={pixabay_api_key}&q={keyword}&image_type=photo&page={page}&per_page={per_page}'
    return requests.get(search_url).json()


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
    last_index = 0 if df.empty else df['index'].max() # Convert to number to find maximum value
    # last_index = 0 if df.empty else df['index'].iloc[-1] # Find last value        
    return str(int(last_index)+1).zfill(6)


if __name__ == '__main__':
    web = re.sub(r'crawler_|.py', '', os.path.basename(__file__))
    category = 'Doodle'

    keyword_list = getattr(keywords, f'{category}_keyword_list')

    for keyword in keyword_list:
        crawler_results(web, category, keyword, time_sleep=6)
