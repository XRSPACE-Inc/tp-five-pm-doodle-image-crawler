import os
import re
import time
from io import BytesIO

import keywords
import pandas as pd
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
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

    options = Options()
    options.add_argument('--headless')  # Run in headless mode (without a GUI)
    driver = webdriver.Firefox(options=options)

    url = f'https://www.shutterstock.com/ja/search/{keyword}'
    pages = get_pages(driver, url)
    
    for page in range(1, pages+1):
        try:
            img_name_list = get_search_resp_results(driver, url, page)
        except Exception as e:
            print(f'Error img_name_list message: {e}')
            continue
        for img_name in img_name_list:
            dl_url = f'https://image.shutterstock.com/z/{img_name}.jpg'
            check_exist_list = get_check_exist_list(archive_path)
            if dl_url in check_exist_list:
                print(f'Url exist: {dl_url}')
            if not dl_url in check_exist_list:
                print(f'Url insert: {dl_url}')
                try:
                    get_dl_img(keyword, source, dl_url, time_sleep, archive_path, archive_columns, source_path)
                except Exception as e:
                    print(f'Error get_dl_img message: {e}')
                    continue
            print('-'*3)
        print('>'*6)
        time.sleep(time_sleep)
    driver.quit()

def get_pages(driver, url):
    driver.get(url)
    pages = driver.find_element(By.CSS_SELECTOR, '.MuiTypography-root.MuiTypography-subtitle2.mui-10a3ukw-totalPages-centerPagination')
    return int(pages.text.replace('/', '').replace(',', ''))

def get_search_resp_results(driver, url, page):
    search_url = f'{url}?page={page}'
    driver.get(search_url)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(3)
    elements = driver.find_elements(By.CSS_SELECTOR, '.mui-t7xql4-a-inherit-link')
    return [elem.get_attribute('href').split('/')[-1] for elem in elements]

def get_dl_img(keyword, source, dl_url, time_sleep, archive_path, archive_columns, source_path):
    date = get_today()
    index = get_index(archive_path)
    file_name = f'{source}_{index}.jpg'
    file_name_path = f'{source_path}/{file_name}'

    resp = requests.get(dl_url)
    content = resp.content
    get_remove_black_strip_to_save(content, file_name_path, black=0.1)

    info_dict = {key: locals()[key] for key in archive_columns}
    print(info_dict)
    df = pd.DataFrame(info_dict, index=[0])
    df.to_csv(archive_path, mode='a', index=False, header=False)
    time.sleep(time_sleep)    

def get_remove_black_strip_to_save(content, file_name_path, black=0.1):
    img = Image.open(BytesIO(content))
    width, height = img.size
    new_height = int(height * (1-black))
    img.crop((0, 0, width, new_height)).save(file_name_path)

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
        crawler_results(web, category, keyword, time_sleep=6)