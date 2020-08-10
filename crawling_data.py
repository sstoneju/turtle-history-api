#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import time
import re
import pdb
import glob
from tqdm import tqdm

LOGGER = logging.getLogger()

def init_logging():
    LOGGER.setLevel(logging.WARN)
    fmt = logging.Formatter('%(asctime)s: %(message)s',
                            '%m/%d/%Y %I:%M:%S %p')
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    LOGGER.addHandler(console)

class Crawler(object):
    def __init__(self):
        LOGGER.info('Init crawler...')

    def crawl_blog(self, url):
        '''
        request http and crawl content
        '''
        # self._agent = requests.Session()
        
        text_res = ''

        url = self._clean_context(url)
        which_blog = self._find_which_blog(url)
        LOGGER.info('tartget_url: %s' %url)

        if which_blog  == 'tistory':
            [title, text_res, tags] = self._crawl_in_tistory(url)
        elif which_blog == 'm.naver':
            [title, text_res, tags] = self._crawl_in_m_naver(url)
        elif which_blog == '':
            LOGGER.info('Error: cant detected blog: {}'.format(url))
            
        plain_text = self._clean_context(text_res)

        result = {
            'url': url,
            'title': self._clean_context(title),
            'document': self._clean_context(plain_text),
            'tags': tags.replace('\n', ' ').strip()
        }

        # close resource.
        # self._agent.close()
        return result

    def crawl_etf(self, ticker='', default_contry='us'):
        '''
        https://stooq.com/q/d/l/?s=qqq.us&i=d
        https://query1.finance.yahoo.com/v7/finance/download/TQQQ?period1=0&period2=1597017600&interval=1d&events=history
        이곳에서 데이터를 받아온다. SHY, QQQ BND, AGG, VWO를 기본적으로 돌릴 수 있게 한다.
        '''
        



        return

    def _find_which_blog(self, url):
        '''
        Find out what kind of site this URL is.
        Includes specific host names and the Web has cookie information.
        '''
        try:
            contain_baseUrl = { 'naver':'m.naver', 'tistory':'tistory' }

            baseUrl = urlparse(url)
            LOGGER.info('base_url: {}'.format(baseUrl.netloc))

            # return currect blog if exist url in dictionary.
            for key, value in contain_baseUrl.items():
                if key in baseUrl.netloc:
                    return value
                else:
                    return 'tistory'
        except Exception as e: # when request time.
            LOGGER.info('Error: {}'.format(e))
        return ''

    def _crawl_in_m_naver(self, url): 
        text = ""
        try:
            headers = { 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36' }
            result = requests.get(url=url, headers = headers)

            html_text = result.text
            soup = BeautifulSoup(html_text, 'html.parser')
            self._remove_html_tag(soup)
            
            title_html1 = soup.select_one('.se-title-text')
            title_html2 = soup.select_one('.se_title')
            title_html3 = soup.select_one('.tit_area')

            html_case_1 = soup.select('.se_component_wrap')
            html_case_2 = soup.select_one('#viewTypeSelector')

            tag = soup.select_one('.post_tag')

            if title_html1: # case 1
                LOGGER.info('title has .se-title-text')
                title = title_html1.text
            elif title_html2: # case 2
                LOGGER.info('title has .se_title')
                title = title_html2.text
            elif title_html3: # case 2
                LOGGER.info('title has .tit_area')
                title = title_html3.text
            else: # case3
                title = 'Not found title!'
            
            if html_case_1: # case 1
                LOGGER.info('Html has .se_component_wrap')
                text += html_case_1[1].text
            elif not html_case_1 and html_case_2: # case 2
                LOGGER.info('Html has #viewTypeSelector')
                text += html_case_2.text
            else: # case3
                text = 'Not found any content_list on m.naver!'

            tag = soup.select_one('.post_tag')
            tags =  tag.text if tag else ''

        except Exception as e:
            return 'Error: {}'.format(e)
        return [title, text, tags]


    def _crawl_in_tistory(self, url):
        text = ""
        try:
            headers = { 'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36' }
            result = requests.get(url=url, headers = headers)

            html_text = result.text
            soup = BeautifulSoup(html_text, 'html.parser')
            self._remove_html_tag(soup)

            title_html = soup.select_one('.tit_blogview')
            html_case_1 = soup.select('.blogview_content')
            html_case_2 = soup.select('[class*="article"]')
            tag_list = soup.select('.list_tag > a')

            title = title_html.text if title_html else ''

            if html_case_1:
                LOGGER.info('Html has .blogview_content')
                for content in html_case_1:
                    text += content.text
            elif not html_case_1 and html_case_2:
                LOGGER.info('Html has [class*="article"]')
                for content in html_case_2:
                    text += content.text
            else:
                text = 'Not found any content_list on tistory!'

            tags = ' '.join([ tag.text for tag in tag_list]) if tag_list else ''
        except Exception as e:
            return 'Error: {}'.format(e)
        return [title, text, tags]

    def _remove_html_tag(self, soup):
        # remove sctipt tag
        [ s.extract() for s in soup.select('script') ]
        # remove usless buttom_info of title
        [ s.extract() for s in soup.select('.blog_authorArea')]
        [ s.extract() for s in soup.select('.blog_btnArea')]

    def _clean_context(self, text):
        # remove tab and zero width space.
        _text = text.replace('\t','')
        _text = _text.replace('\u200b','')

        # remove enter to dot.
        _text = re.compile('\s\\n+').sub(' ', _text)
        _text = re.compile('\\.\\n').sub('.', _text)
        _text = re.compile('[\\.]').sub('.', _text)
        # _text = re.compile(r'[.]/g').sub('.', _text)

        # remove usless code.
        _text = re.compile('{.*?}').sub('', _text)
        _text = re.compile('<a.*?</a>').sub('', _text)

        # remove emoji
        EMOJI_PATTERN = re.compile(
            "["
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "]+"
        )

        _text = re.sub(EMOJI_PATTERN, ' ', _text)
        # emoji trash code.
        _text = re.compile('\ud835').sub(' ', _text)
        _text = _text.strip()
        return _text


def main(args):
    input_dir = args.input_dir
    output_dir = args.output_dir

    # instance class
    myCrawler = Crawler()
    
    # load input data
    input_files = glob.glob('{}/*.json'.format(input_dir))
    
    for input_file in tqdm(input_files, total=len(input_files)):
        with open(input_file, encoding='utf-8', errors='surrogatepass') as f:
            input_data = json.load(f)['data']

        for row in tqdm(input_data, total=len(input_data)):
            for blog in row['blog_data']:
                # if the blog is already crawled, skip it.
                if 'document' in blog and not blog['document'].startswith('Not found'):
                    continue
                url = blog['url']
                result = myCrawler.crawl_blog(url)
                blog['document'] = result['document']
                blog['title'] = result['title']
                blog['tags'] = result['tags']
                blog['quality_check'] = -1
            
        output = {
            'data' : input_data
        }

        # save result
        with open(input_file, mode='w', encoding='utf-8', errors='surrogatepass') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    init_logging()

    # Required
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', required=True)
    parser.add_argument('--output_dir', required=True)
    args = parser.parse_args()

    main(args)