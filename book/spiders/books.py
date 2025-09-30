from pathlib import Path

import scrapy
from scrapy.http import Response, response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):

        categories = response.css("div.side_categories ul li ul li a")
        for cat in categories:
            category_name = cat.css("::text").get().strip()
            category_url = response.urljoin(cat.attrib["href"])
            yield scrapy.Request(
                category_url,
                callback=self.parse_category,
                cb_kwargs={"category": category_name},
            )

    def parse_category(self, response: Response, category):
        books = response.css("article.product_pod h3 a::attr(href)").getall()
        for book in books:
            yield response.follow(
                book,
                callback=self.parse_book,
                cb_kwargs={"category": category}
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse_category,
                cb_kwargs={"category": category}
            )

    def parse_book(self, response: Response, category):
        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": response.css("p.instock.availability::text").get(),
            "rating": response.css("p.star-rating::attr(class)").get(),
            "category": category,
            "description": response.css("#product_description ~ p::text").get(),
            "upc": response.css("table.table tr:nth-child(1) td::text").get(),
        }