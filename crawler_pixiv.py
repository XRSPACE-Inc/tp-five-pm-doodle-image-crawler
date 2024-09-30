# Real img
# 'https://i.pximg.net/img-original/img/2009/04/16/14/19/22/3885860_p0.jpg'
# 'https://i.pximg.net/img-master/img/2009/04/16/14/19/22/3885860_p0_master1200.jpg'
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
        for img_url in img_url_list:
            dl_url = img_url.replace('/c/250x250_80_a2', '').replace('_square1200', '_master1200')
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
    search_url = f'https://www.pixiv.net/ajax/search/illustrations/chibi?word=chibi&s_mode=s_tag_full&p={page}'
    headers = get_headers()
    resp = requests.get(search_url, headers=headers)
    resp_results = resp.json()
    illust = resp_results['body']['illust']
    pages = illust['lastPage']
    img_url_list = [i['url'] for i in illust['data']]
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
        'Cookie': 'first_visit_datetime_pc=2024-07-23%2016%3A38%3A57; p_ab_id=4; p_ab_id_2=2; p_ab_d_id=1217497867; yuid_b=GGdZUCM; cf_clearance=N.zpuT88aD9d3NIeuRwXYmMJlTPTNcOPoM9B6E6Ys38-1722389666-1.0.1.1-QpM6Aaf9Xr3vUaGKbiG9EoqASukRlmEDTwIizjQs1_W2nF4_yoTJY1VoJ1VUFwzUBm60bbQldbqylfMetHlN8A; privacy_policy_agreement=7; _ga_75BBYNYN9J=deleted; _gid=GA1.2.730994282.1722568765; device_token=00edef3f3bb61bebafd8481a64c736ad; c_type=40; privacy_policy_notification=0; a_type=0; b_type=1; _gcl_au=1.1.1930878242.1722570243; cc1=2024-08-02%2014%3A56%3A27; PHPSESSID=108482747_up5dPs1Ue0F9glOnFLIx39i6eUMCKE0X; _ga_MZ1NL4PHH0=GS1.1.1722578192.3.1.1722578224.0.0.0; _ga_75BBYNYN9J=GS1.1.1722586488.3.0.1722586493.0.0.0; _ga=GA1.2.1959985969.1721720340; __cf_bm=Gy4lLWARKo4wPPiBPO5vUiHjKBa7B5pl9dBnkHp6ldA-1722587987-1.0.1.1-yljqCNz0DxhmM.JqEJkUkhnW5oKDNgSB7f2VDjVzgoMeGeyAnPE5FbIFyxTD6nIuszVtAb0WejGcKy9Wh_vCnp0T_Gr1qTT4tbonCl4jPCg',
        'Referer': 'https://www.pixiv.net',
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
        crawler_results(web, category, keyword, time_sleep=2)