from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def crawl_books():
    url = 'https://books.toscrape.com/catalogue/page-1.html'
    client = MongoClient('mongodb+srv://phongthanh:thangkhung0993@cluster0.3nqvlv3.mongodb.net/?appName=Cluster0')

    db = client["book_db"]
    mongo = db["books"]
    current_url = url
    page_count = 1
    while True:
        print(f"Dang cao du lieu tu {current_url}")
        try:
            response = requests.get(current_url,timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"There is an error: {e}")
            break
        soup = BeautifulSoup(response.text,'lxml')
        books = soup.select('.product_pod')
        for book in books:
            new_book = {}
            new_book['title'] = book.select_one('h3 >a')['title']
            new_book['price'] = book.select_one('.price_color').text.replace('Â','')
            new_book['star'] = book.select_one('.star-rating')['class'][1]
            new_book['is_stock'] = book.select_one('.instock.availability').get_text(strip=True)
            mongo.insert_one(new_book)
        next_button = soup.select_one('.next > a')
        if next_button:
            current_url = urljoin(current_url,next_button['href'])
            page_count +=1
        else:
            print(f"Da duyet xong tong cong {page_count} page")
            break

if __name__ == "__main__":
    crawl_books()
