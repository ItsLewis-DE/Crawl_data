from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs,urljoin
import time
import random
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
from dotenv import load_dotenv
from pathlib import Path
import os
load_dotenv()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    raise ValueError("MONGO_URI is not set in environment variables.")

client = MongoClient(mongo_uri)
db = client["article_db"]
mongo = db["articles"]
db_comment = client['comment_db']
mongo_comment = db_comment['comments']

url = 'https://news.ycombinator.com/news'

session = requests.Session()
session.headers.update(headers)

import sys

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'WARNING': '\033[33m', # Yellow
        'INFO': '\033[32m',    # Green
        'DEBUG': '\033[36m',   # Cyan
        'CRITICAL': '\033[31m',# Red
        'ERROR': '\033[31m'    # Red
    }
    RESET = '\033[0m'

    def format(self, record):
        log_fmt = f"{self.COLORS.get(record.levelname, self.RESET)}%(asctime)s - %(name)s - %(levelname)s - %(message)s{self.RESET}"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

APP_DIR = Path(__file__).resolve().parent
log_dir = APP_DIR / 'job_web'
log_dir.mkdir(parents=True, exist_ok=True)
DEFAULT_LOG_FILE = log_dir / 'app.log'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(DEFAULT_LOG_FILE, mode='a', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredFormatter())
logger.addHandler(console_handler)
def crawl_jobs(url):
    article_count = 1 
    retry = 0
    while article_count <= 20:
        if retry >5:
            break
        logger.info(f"Extracting data from page: {article_count}")
        try:
            response = session.get(url,timeout=30)
            if response.status_code == 429:
                logger.warning("Rate limited. Sleeping...")
                time.sleep(60)
                retry +=1
                continue
            response.raise_for_status()
            data_raw = response.text
        except requests.exceptions.RequestException as e:
            logger.warning(f"There is an error: {e}")
            retry +=1
            time.sleep(60)
            continue
        soup = BeautifulSoup(data_raw,'lxml')
        for article in soup.select('.athing.submission'):
            one_article = {}
            one_article['title'] = article.select_one('.titleline >a').get_text(strip=True)
            one_article['post_id'] = article.get('id')
            source_link_tag = article.select_one('.sitebit.comhead > a')
            if source_link_tag:
                one_article['source'] = source_link_tag.get('href')
            else:
                one_article['source'] = 'no_source'
            subtext_row = article.find_next_sibling('tr')
            core = subtext_row.select_one('.score')
            if core:
                one_article['score'] = subtext_row.select_one('.score').text
            author = subtext_row.a
            if author:
                one_article['author'] = subtext_row.a.text          
            mongo.update_one(
                {'post_id':one_article['post_id']},
                {'$set':one_article},
                upsert=True
            )
        next_button = soup.select_one('.morelink')
        if next_button:
            next_link = next_button['href']
            url = urljoin(url,next_link)
            article_count +=1 
        else:
            break
        time.sleep(random.uniform(10,20))
def crawl_link_comment(url):
    page = 1
    retry = 0
    retry_comment =0
    while page <= 20:
        if retry > 5:
            logger.error("Error")
            break
        if retry_comment >5:
            logger.error("Error")
            break
        logger.info(f"Extracting comments from page: {page}")
        try:
            response = session.get(url, timeout=30)
            if response.status_code == 429:
                logger.warning("Rate limited. Sleeping...")
                time.sleep(60)
                retry += 1
                continue
            response.raise_for_status()
            data = response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            retry += 1
            time.sleep(10)
            continue
            
        try:
            soup = BeautifulSoup(data, 'lxml')
            next_button = soup.select('.subline > a:last-of-type')
            more_button = soup.select_one('.morelink')
            
            for a in next_button:
                next_button_text = a.text
                next_button_link = a['href']
                new_url = urljoin(url, next_button_link)
                if next_button_text != 'discuss':
                    article_id = next_button_link.split('=')[-1]
                    logger.info(f"Crawl data article: {article_id}")
                    try:
                        retry_comment += crawl_comment(new_url, article_id)
                    except Exception as e:
                        logger.error(f"Error calling crawl_comment for {article_id}: {e}")
                        
            if more_button:
                more_link = more_button['href']
                url = urljoin(url, more_link)
                page += 1 
                retry = 0
            else:
                break
        except Exception as e:
            logger.error(f"Error parsing page {page}: {e}")
            page += 1
        time.sleep(random.uniform(5, 10))
    logger.info("Load data into mongodb successfully")


def crawl_comment(url, article_id):
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        data_2 = response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching comments for article {article_id}: {e}")
        time.sleep(60)
        return 1
    try:
        soup = BeautifulSoup(data_2, 'lxml')
        comments_data = soup.select('.athing.comtr')
        comment_count = 1 
        for c in comments_data:
            logger.info(f"Extracting comment {comment_count}")
            try:
                comments = {}
                if comment_count == 1:
                    comments['article_id'] = article_id
                elif comment_count == 10:
                    break
                comments['comment_id'] = c['id']
                navigation = c.select('.navs >a')
                if navigation and navigation[0].text == 'parent':
                    comments['parent_comment_id'] = navigation[0]['href'].replace('#', '')
                else:
                    comments['parent_article_id'] = article_id
                    
                author_tag = c.select_one('.comhead > a')
                comments['author'] = author_tag.text if author_tag else 'unknown'
                
                text_tag = c.select_one('.commtext')
                comments['text'] = text_tag.text if text_tag else ''
                
                mongo_comment.update_one(
                    {'comment_id' : comments['comment_id']},
                    {'$set':comments},
                    upsert=True
                )
            except Exception as e:
                logger.error(f"Error parsing comment {comment_count}: {e}")
                return 1
            comment_count += 1
        return 0

    except Exception as e:
        logger.error(f"Error parsing comments page for article {article_id}: {e}")
        return 1

# crawl_jobs(url)
crawl_link_comment(url)