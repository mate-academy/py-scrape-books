import re
from pathlib import Path

import scrapy
from scrapy.http import Response


class SpyderBooksSpider(scrapy.Spider):
    name = "spyder_books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/unicorn-tracks_951/index.html"]

    def parse(self, response: Response, **kwargs):
        p_element = response.css('p.instock.availability')
        p_html = p_element.get()
        match = re.search(r'(\d+) available', p_html)
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css(".price_color::text").get(),
            "amount_in_stock": match.group(1),
            "rating": len(response.css(".Three .icon-star").getall()),
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("#product_description+ p::text").get(),
            "upc": response.css("tr:nth-child(1) td::text").get()

        }
