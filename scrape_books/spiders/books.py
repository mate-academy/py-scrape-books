import scrapy
from scrapy.http import Response
from urllib.parse import urljoin


class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['https://books.toscrape.com/']

    # @staticmethod
    # def get_urls_for_all_books_in_page(response: Response):
    #     return [url.css(".image_container > a ::attr(href)").get() for url in response.css(".col-xs-6")]

    def parse(self, response: Response, **kwargs):
        # all_urls = self.get_urls_for_all_books_in_page(response)

        for book in response.css(".col-xs-6"):
            yield {
                "title": book.css(".product_pod > h3 > a::attr(title)").get(),
                "price": book.css(".price_color::text").get(),
                "url": book.css(".image_container > a ::attr(href)").get()
            }

        # for url in all_urls:
        #     book_url = urljoin(self.start_urls[0], url)
        #     yield {
        #         "title": response.css("div.col-sm-6.product_main > h1::text").get(),
        #         # "price": book.css(".price_color::text").get(),
        #         # "url": book.css(".image_container > a ::attr(href)").get()
        #     }
        #     yield scrapy.Request(book_url, callback=self.parse)

