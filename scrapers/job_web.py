from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs,urljoin
import time
import random
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}
client = MongoClient('mongodb+srv://thanhphong:thangkhung0993@cluster0.eunottz.mongodb.net/?appName=Cluster0')
db = client["article_db"]
mongo = db["articles"]
db_comment = client['comment_db']
mongo_comment = db_comment['comments']
url = 'https://news.ycombinator.com/news'
session = requests.Session()
session.headers.update(headers)
def crawl_jobs(url):
    page_count = 1 
    while page_count <= 10:
        print(f"Extracting data page {url}")
        try:
            response = session.get(url,timeout=30)
            if response.status_code == 429:
                print("Rate limited. Sleeping...")
                time.sleep(60)
                continue
            response.raise_for_status()
            data_raw = response.text
        except requests.exceptions.RequestException as e:
            print(f"There is an error: {e}")
            break
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
            mongo.insert_one(one_article)
        next_button = soup.select_one('.morelink')
        if next_button:
            next_link = next_button['href']
            url = urljoin(url,next_link)
            page_count +=1 
        else:
            break
        time.sleep(random.uniform(5,7))
def crawl_link_comment(url):
    response = session.get(url,timeout=30)
    data = response.text
    soup = BeautifulSoup(data,'lxml')
    next_button = soup.select('.subline > a:last-of-type')
    for a in next_button:
        next_button_text = a.text
        next_button_link = a['href']
        new_url = urljoin(url,next_button_link)
        if next_button_text != 'discuss':
            article_id = next_button_link.split('=')[-1]
            print(f"Crawl data article: {article_id}")
            crawl_comment(new_url,article_id)
    print("Load data into mongodb successfully")


def crawl_comment(url,article_id):
    response = session.get(url,timeout=30)
    data_2 = response.text
    soup = BeautifulSoup(data_2,'lxml')
    comments_data = soup.select('.athing.comtr')
    comment_count =1 
    for c in comments_data:
        print(f"Extracting comment {comment_count}")
        comments = {}
        if comment_count==1:
            comments['article_id'] = article_id
        elif comment_count ==10:
            break
        comments['comment_id'] = c['id']
        author = c.select_one('.comhead > a').text
        comments['author'] = author
        comments['text'] = c.select_one('.commtext').text
        mongo_comment.insert_one(comments)
        comment_count+=1
crawl_jobs(url)
crawl_link_comment(url)
