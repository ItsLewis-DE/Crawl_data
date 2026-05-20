# Dự Án Crawl Data (Cào Dữ Liệu)

Dự án này được tạo ra với mục đích **luyện tập và nâng cao kỹ năng cào dữ liệu (web scraping)** bằng Python từ cơ bản đến nâng cao. Các script trong dự án chủ yếu phục vụ cho việc học tập cá nhân, thử nghiệm các kỹ thuật bóc tách dữ liệu trên các trang web mẫu và cách kết nối, lưu trữ thông tin vào cơ sở dữ liệu.


## 📁 Cấu trúc dự án

- `book_crawl.py`: Script thực hành cào dữ liệu các cuốn sách từ trang [books.toscrape.com](https://books.toscrape.com/). Xử lý tự động chuyển trang (pagination), bóc tách các thông tin của sách (tiêu đề, giá bán, đánh giá sao, tình trạng kho) và thực hành lưu trực tiếp vào cơ sở dữ liệu MongoDB.
- `web.py`: Script thực hành cào dữ liệu các câu trích dẫn (quotes) từ trang [quotes.toscrape.com](https://quotes.toscrape.com/). Bóc tách thông tin chi tiết về nội dung trích dẫn, tên tác giả, đường dẫn URL tác giả và các thẻ tag liên quan.
- `main.py`: File chạy chính mặc định.
- `pyproject.toml` / `uv.lock`: File quản lý danh sách các package đã được sử dụng trong quá trình thực hành (bao gồm `requests`, `beautifulsoup4`, `lxml`, `pymongo`, v.v.).

## 🎯 Mục tiêu học tập đạt được

- Hiểu và áp dụng thư viện `requests` để gửi các HTTP requests lấy mã nguồn trang web.
- Thành thạo việc tìm kiếm, phân tích và trích xuất dữ liệu từ cây DOM (HTML) sử dụng `BeautifulSoup` và parser `lxml`.
- Làm quen với thao tác cơ sở dữ liệu NoSQL: kết nối và chèn dữ liệu vào MongoDB thông qua `pymongo`.
- Xử lý các luồng cào dữ liệu thực tế như: bóc tách dữ liệu theo khối (từng sách, từng trích dẫn), cào dữ liệu qua nhiều trang liên tiếp và làm sạch dữ liệu cơ bản (ví dụ: loại bỏ ký tự rác khi lấy giá tiền).
