import scrapy
from scrapy.http import Response
import re


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def _parse_rating(self, response):
        classes = response.css("p.star-rating").attrib.get("class", "").split()
        ratings = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        for cls in classes:
            if cls in ratings:
                return ratings[cls]
        return 0

    def parse(self, response: Response, **kwargs):
        products = response.css("article.product_pod")
        if not products:
            self.logger.warning("No products found on page")

        for product in products:
            book_url = product.css("h3 a::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_book)
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response):
        stock_text = response.css("p.instock.availability::text").getall()
        clean_stock_text = " ".join(stock_text).strip()

        amount = int(re.search(r"\d+", clean_stock_text).group())

        yield {
            "title": response.css("h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "amount_in_stock": amount,
            "rating": self._parse_rating(response),
            "description": response.css("#product_description ~ p::text").get(),
            "upc": response.css("table tr:nth-child(1) td::text").get()
        }
