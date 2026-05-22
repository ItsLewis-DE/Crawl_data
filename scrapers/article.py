from bs4 import BeautifulSoup
import requests

def crawl_articles():
    url = 'https://quotes.toscrape.com/'
    content = requests.get(url,timeout=30)
    soup = BeautifulSoup(content.text,'lxml')
    articles = []
    for article in soup.find_all('div',class_='quote'):
        data = {}
        quote = article.find('span',class_='text')
        data['quote'] = quote.text
        author = article.find('small',class_='author')
        data['author'] = author.text
        author_url = article.a['href']
        data['author_url'] = author_url
        data['tag'] = []
        for tag in article.find_all('a',class_='tag'):
            data['tag'].append(tag['href'])
        articles.append(data)
    for article in articles:
        print(article)

if __name__ == "__main__":
    crawl_articles()
