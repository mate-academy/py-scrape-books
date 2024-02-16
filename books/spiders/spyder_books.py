import re

import scrapy
from scrapy.http import Response


class SpyderBooksSpider(scrapy.Spider):
    name = "spyder_books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for url in response.css(".nav-list ul li  a::attr(href)").getall():
            yield response.follow(url=url, callback=self.parse_one_genre)

    def parse_one_genre(self, response: Response):
        for url in response.css(".product_pod > h3 > a::attr(href)").getall():
            yield response.follow(url=url, callback=self.parse_one_book_details)
        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_one_genre)

    def parse_one_book_details(self, response: Response, **kwargs):
        p_element = response.css('p.instock.availability')
        p_html = p_element.get()
        match = re.search(r'(\d+) available', p_html)
        item = {
            "title": response.css("h1::text").get(),
            "price": response.css(".price_color::text").get(),
            "amount_in_stock": match.group(1),
            "rating": len(response.css(".Three .icon-star").getall()),
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("#product_description+ p::text").get(),
            "upc": response.css("tr:nth-child(1) td::text").get()

        }
        yield item
