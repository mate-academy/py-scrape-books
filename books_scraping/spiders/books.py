from enum import Enum

import scrapy
from scrapy.http import Response

from books_scraping.items import BooksScrapingItem


class Rating(Enum):
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        book_links = response.css("article.product_pod h3 a::attr(href)").getall()

        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response):
        title = response.css("div.product_main h1::text").get()
        price = float(response.css("p.price_color::text").get().replace("£", ""))

        in_stock_text = response.xpath(
            '//th[text()="Availability"]/following-sibling::td/text()'
        ).get()
        amount_in_stock = int(in_stock_text.replace("In stock (", "").replace(" available)", ""))

        rating_text = response.css("p.star-rating::attr(class)").get().split()[-1]
        rating = Rating[rating_text].value

        category = response.css("ul.breadcrumb li a::text").getall()[-1]
        description = response.css("#product_description + p::text").get(default="")
        upc = response.xpath(
            '//th[text()="UPC"]/following-sibling::td/text()'
        ).get()

        yield BooksScrapingItem(
            title=title,
            price=price,
            amount_in_stock=amount_in_stock,
            rating=rating,
            category=category,
            description=description,
            upc=upc,
        )
