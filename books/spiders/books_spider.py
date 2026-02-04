import scrapy
from scrapy.http import Response
from scrapy.loader import ItemLoader

from books.items import BooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs):
        book_page_links = response.css(".image_container *::attr(href)")
        yield from response.follow_all(book_page_links, self._parse_book)

        pagination_links = response.css("li.next > a::attr(href)")
        yield from response.follow_all(pagination_links, self.parse)


    def _parse_book(self, response: Response):
        loader = ItemLoader(item=BooksItem(), response=response)

        loader.add_css("title", ".product_main > h1::text")
        loader.add_css("price", ".price_color::text")
        loader.add_xpath(
            "amount_in_stock",
            "//th[contains(text(), 'Availability')]/following-sibling::td/text()"
        )
        loader.add_css("rating", ".star-rating::attr(class)")
        loader.add_css("category", ".breadcrumb > li:nth-child(3) > a::text")
        loader.add_css("description", ".product_page > p::text")
        loader.add_xpath(
            "upc",
            "//th[contains(text(), 'UPC')]/following-sibling::td/text()"
        )

        yield loader.load_item()
