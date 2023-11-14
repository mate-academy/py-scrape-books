import scrapy

from scrapy import Selector
from scrapy.http import Response
from word2number import w2n

class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            detail_url = book.css("h3 a::attr(href)").get()
            yield response.follow(detail_url, callback=self.parse_one_book)
        next_page = response.css("li.next a::attr(href)").get()
        yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_one_book(response: Selector):
        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css(".price_color::text").re_first(r"[\d.]+")),
            "amount_in_stock": response.css(".instock").re_first(r"\d+"),
            "rating": w2n.word_to_num(response.css("p.star-rating::attr(class)").get().split()[1]),
            "category": response.css(".breadcrumb li:nth-last-child(2) a::text").get(),
            "description": response.css("article > p::text").get(),
            "upc": response.css(".table-striped tr th:contains('UPC') + td::text").get(),
        }
