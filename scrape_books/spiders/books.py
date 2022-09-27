from urllib.parse import urljoin

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['https://books.toscrape.com/']

    @staticmethod
    def get_urls_for_all_books_in_page(response: Response):
        return [url.css(".image_container > a ::attr(href)").get() for url in response.css(".col-xs-6")]

    def parse(self, response: Response, **kwargs):
        all_urls = self.get_urls_for_all_books_in_page(response)

        yield {
            "title": response.css(".product_pod > h3 > a::attr(title)").get(),
            "price": response.css(".price_color::text").get(),
            # "amount_in_stock": response.css(".instock::text").get(),
            # "rating": "1",
            # "category": "2",
            # "description": "3",
            # "upc": 4,
        }

        for url in all_urls:
            book_url = urljoin(self.start_urls[0], url)

            yield scrapy.Request(book_url, callback=self.parse)

