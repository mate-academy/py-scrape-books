import re

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/category/books_1/page-1.html"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_url = response.urljoin(book.css("h3 > a::attr(href)").get())
            yield scrapy.Request(book_url, callback=self._parse_book_from_detail_page)

        next_page = response.css("ul > li.next > a::attr(href)").get()
        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def _parse_book_from_detail_page(self, response: Response) -> dict:
        title = response.css("h1::text").get()
        price_content = response.css("p.price_color::text").get() or "£666"
        price = float(price_content.replace("£", ""))

        availability_text = response.css("p.instock.availability").get() or "666"
        amount_in_stock = re.search(r"\d+", availability_text).group()

        rating_class = response.css("p.star-rating::attr(class)").get() or "No rating"
        rating = rating_class.split()[-1]
        rating_value = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }.get(rating, 0)

        category = response.css("ul > li:nth-child(3) > a::text").get() or "No category"
        description = response.css("article > p::text").get() or "No description"

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating_value,
            "category": category,
            "description": description
        }
