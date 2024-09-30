import os
import time
from datetime import datetime

import pandas as pd


def timer(func):
    def wrap(*args, **kwargs):
        start_time_dt =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        start_time = time.time()
        print('='*30)

        func(*args, **kwargs)

        end_time = time.time()
        end_time_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cost_time = end_time-start_time
        m, s = divmod(cost_time, 60)
        h, m = divmod(m, 60)
        cost_time_dt = f'{int(h)}h:{int(m)}m:{round(s, 2)}s'

        print('='*30)
        print('start_time:', start_time_dt)
        print('end_time  :', end_time_dt)
        print('cost_time :', cost_time_dt)
    return wrap


def cuda_status():
    import torch; print(torch.cuda.is_available())


def get_folder_path(pre_path, folder_name):
    folder_path = f'{pre_path}/{folder_name}'
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def get_archive_path(pre_path, archive_columns, source, today=None):
    archive_path = f'{pre_path}/archive_{source}_{today}.csv' if today else f'{pre_path}/archive_{source}.csv'
    if not os.path.exists(archive_path):
        df = pd.DataFrame(archive_columns)
        df.to_csv(archive_path, index=False)
    return archive_path


def get_today():
    return datetime.strftime(datetime.now(), '%Y%m%d')


def get_current_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_archive_columns():
    return {'keyword': [], 'source': [], 'index': [], 'file_name': [], 'date': [], 'dl_url': []}