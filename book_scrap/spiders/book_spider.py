from typing import Generator

import scrapy
from scrapy.http import Response

RATING_LIST = {
    "One": "1",
    "Two": "2",
    "Three": "3",
    "Four": "4",
    "Five": "5",
    "Zero": "0",
}


class BookSpider(scrapy.Spider):
    name = "book_spider"
    start_urls = ['https://books.toscrape.com/']

    @staticmethod
    def parse_book(page: Response) -> Generator:
        yield{
            "title": page.css(".product_main > h1::text").get(),
            "price": page.css(".price_color::text").get(),
            "amount_in_stock": page.css(".instock").get().split()[7][1:],
            "rating": RATING_LIST[page.css(".star-rating::attr(class)").get().split()[1]],
            "category": page.css(".breadcrumb > li:nth-child(3) > a::text").get(),
            "description": page.css("#product_description + p::text").get(),
            "upc": page.css(".table.table-striped > tr:nth-child(1) > td::text").get(),
        }

    def parse(self, response: Response, **kwargs) -> Generator:
        for book in response.css(".product_pod > h3 > a::attr(href)").getall():
            yield scrapy.Request(url=response.urljoin(book), callback=self.parse_book)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)
