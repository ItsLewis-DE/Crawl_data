# Dự Án Crawl Data (Cào Dữ Liệu)

Đây là một dự án Python dùng để thu thập (cào) dữ liệu từ các trang web mẫu bằng cách sử dụng `requests` và `BeautifulSoup`. Dữ liệu sau khi thu thập có thể được xuất ra màn hình hoặc lưu trữ vào cơ sở dữ liệu MongoDB.

## 📁 Cấu trúc dự án

- `scrapers/book_crawl.py`: Script dùng để cào dữ liệu các cuốn sách từ trang [books.toscrape.com](https://books.toscrape.com/). Tự động chuyển trang, lấy các thông tin của sách (tiêu đề, đánh giá sao, tình trạng kho) và lưu vào cơ sở dữ liệu MongoDB.
- `scrapers/article.py`: Script dùng để cào dữ liệu các câu trích dẫn (quotes) từ trang [quotes.toscrape.com](https://quotes.toscrape.com/). Lấy thông tin chi tiết về nội dung trích dẫn, tác giả, đường dẫn URL tác giả và các thẻ tag (tags) liên quan.
- `scrapers/job_web.py`: Script dùng để cào dữ liệu từ [news.ycombinator.com](https://news.ycombinator.com/) (Hacker News). Lấy bài viết và lưu vào cơ sở dữ liệu MongoDB.
- `tests/test.py`: Thư mục và file chứa các script thử nghiệm.
- `main.py`: File chạy chính mặc định của dự án. Giao diện dòng lệnh để chọn và chạy các script cào dữ liệu.
- `pyproject.toml` / `uv.lock`: File cấu hình quản lý các package và dependencies của dự án bằng `uv`.
