import re

import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs: dict) -> None:
        for book in response.css("article.product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_book_detail)

        for next_page in response.css("li.next a"):
            yield response.follow(next_page, self.parse)

    def parse_book_detail(self, response: Response) -> None:
        title = response.css("div.product_main h1::text").get()
        price = response.css(
            "div.product_main p.price_color::text"
        ).get().replace("£", "")
        amount_in_stock_text = "".join(
            response.css("p.instock.availability::text").getall()
        ).strip()
        numbers = re.findall(r"\d+", amount_in_stock_text)
        amount_in_stock = numbers[0] if numbers else "0"
        rating = (
            response.css("p.star-rating::attr(class)")
            .get().replace("star-rating", "").strip()
        )
        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        description = response.css("div#product_description + p::text").get()
        upc = response.css("table th:contains('UPC') + td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
