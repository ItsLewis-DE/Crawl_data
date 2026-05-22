from scrapers.job_web import crawl_jobs
from scrapers.article import crawl_articles
from scrapers.book_crawl import crawl_books

def main():
    print("Welcome to Crawl Data Project!")
    print("1. Crawl Jobs (HackerNews)")
    print("2. Crawl Articles (Quotes)")
    print("3. Crawl Books (Books to Scrape)")
    
    choice = input("Enter your choice (1/2/3): ")
    if choice == '1':
        crawl_jobs()
    elif choice == '2':
        crawl_articles()
    elif choice == '3':
        crawl_books()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
