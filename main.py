import importlib
import sys

import keywords


def main(web, category, keyword_list, time_sleep):
    crawler_module = importlib.import_module(f'crawler_{web}')
    for keyword in keyword_list:
        try:
            crawler_module.crawler_results(web, category, keyword, time_sleep)
        except Exception as e:
            print(f'web: {web}, Error message: {e}')
            continue

if __name__ == '__main__':
    web = sys.argv[1]  # flickr, freepik, pexels, pikbest, pinterest, pixabay, pixiv, shutterstock, unsplash
    # category = 'HumanFace'
    category = 'Doodle'
    keyword_list = getattr(keywords, f'{category}_keyword_list')

    main(web, category, keyword_list, time_sleep=3)
