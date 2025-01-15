import scrapy
from scrapy.http import Response

from ..items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css("article.product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            full_book_url = response.urljoin(book_url)
            yield response.follow(
                full_book_url,
                callback=self.parse_book_details
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(self, response: Response, **kwargs) -> BookItem:
        yield BookItem(
            title=response.css("h1::text").get(),
            price=response.css(".price_color::text").get(),
            amount_in_stock=response.css("tr:nth-child(6) > td::text").get(),
            rating=response.css(".star-rating::attr(class)").get(),
            category=response.css(
                "ul.breadcrumb li:nth-child(3) a::text"
            ).get(),
            description=response.xpath(
                "//div[@id='content_inner']/article/p/text()"
            ).get(),
            upc=response.css(
                "table.table.table-striped tr:nth-child(1) td::text"
            ).get(),
        )
