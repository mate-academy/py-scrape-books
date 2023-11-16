import scrapy
from scrapy import Selector
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    rating_mapping = {
        "Zero": 0,
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            yield response.follow(
                book.css("h3 a::attr(href)").get(),
                callback=self.parse_detail_book_data
            )
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_detail_book_data(self, book: Selector):
        yield {
            "title": book.css(".product_main > h1::text").get(),
            "price": float(book.css(".price_color::text").get().replace("£", "")),
            "amount_in_stock": int(book.css(".instock::text").re_first(r"\d+")),
            "rating": self.rating_mapping[
                book.css(".star-rating::attr(class)").get().split(" ")[1]
            ],
            "category": book.css(".breadcrumb li:nth-child(3) a::text").get(),
            "description": book.css("article > p::text").get(),
            "upc": book.css(".table td::text").get(),
        }
