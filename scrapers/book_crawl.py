from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import logging
from dotenv import load_dotenv

load_dotenv()

import sys
from pathlib import Path

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
log_dir = APP_DIR / 'book_web'
log_dir.mkdir(parents=True, exist_ok=True)
DEFAULT_LOG_FILE = log_dir / 'app.log'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(DEFAULT_LOG_FILE, mode='a')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredFormatter())
logger.addHandler(console_handler)

def crawl_books():
    url = 'https://books.toscrape.com/catalogue/page-1.html'
    
    mongo_uri = os.getenv('BOOK_MONGO_URI')
    if not mongo_uri:
        raise ValueError("BOOK_MONGO_URI is not set in environment variables.")
        
    client = MongoClient(mongo_uri)

    db = client["book_db"]
    mongo = db["books"]
    current_url = url
    page_count = 1
    while True:
        logger.info(f"Dang cao du lieu tu {current_url}")
        try:
            response = requests.get(current_url,timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"There is an error: {e}")
            break
            
        try:
            soup = BeautifulSoup(response.text,'lxml')
            books = soup.select('.product_pod')
            for book in books:
                try:
                    new_book = {}
                    new_book['title'] = book.select_one('h3 >a')['title']
                    new_book['price'] = book.select_one('.price_color').text.replace('Â','')
                    new_book['star'] = book.select_one('.star-rating')['class'][1]
                    new_book['is_stock'] = book.select_one('.instock.availability').get_text(strip=True)
                    mongo.insert_one(new_book)
                except Exception as e:
                    logger.error(f"Error parsing a book: {e}")
                    
            next_button = soup.select_one('.next > a')
            if next_button:
                current_url = urljoin(current_url,next_button['href'])
                page_count +=1
            else:
                logger.info(f"Da duyet xong tong cong {page_count} page")
                break
        except Exception as e:
            logger.error(f"Error parsing page {current_url}: {e}")
            break

if __name__ == "__main__":
    crawl_books()
