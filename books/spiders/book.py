import re
import scrapy
from books.items import BooksItem  # імпорт нашого Item

class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response, **kwargs):
        for book in response.css("ol.row > li"):
            book_url = book.css("h3 a::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_detail_page)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_detail_page(self, response):
        item = BooksItem()
        item["title"] = response.css(".product_main h1::text").get()
        price_text = response.css(".price_color::text").get()
        item["price"] = float(price_text.replace("£", "").strip()) if price_text else 0.0

        availability_text = "".join(response.css(".product_main .availability::text").getall()).strip()
        item["amount_in_stock"] = int(re.search(r"\d+", availability_text).group()) if re.search(r"\d+", availability_text) else 0

        item["description"] = response.css("article.product_page > p::text").get()
        item["upc"] = response.css("th:contains('UPC') + td::text").get()
        item["category"] = response.css(".breadcrumb li:nth-child(3) a::text").get()

        rating_class = response.css(".product_main .star-rating::attr(class)").get()
        rating_text = rating_class.replace("star-rating", "").strip() if rating_class else ""
        rating_text_to_number = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        item["rating"] = rating_text_to_number.get(rating_text, 0)

        yield item
