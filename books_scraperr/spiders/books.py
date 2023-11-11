import scrapy
from scrapy import Selector
from scrapy.http import Response

from word2number import w2n


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        books = response.css(".product_pod")
        for book in books:
            yield scrapy.Request(
                url=self._get_book_url(response, book),
                callback=self._parse_book,
            )
        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _parse_book(response: Response) -> dict:
        def get_rating(response: Response) -> int:
            rating_word = (
                response.css(".star-rating::attr(class)")
                .get()
                .split(" ")
                .pop()
            )
            return w2n.word_to_num(rating_word)

        def get_amount(response: Response) -> int:
            return int(
                response.css(".instock.availability::text").re_first(r"\d+")
            )

        def get_price(response: Response) -> int:
            return int(response.css(".price_color::text").re_first(r"\d+"))

        book_info = {
            "title": response.css("h1::text").get(),
            "price": get_price(response),
            "amount_in_stock": get_amount(response),
            "rating": get_rating(response),
            "category": response.css(
                ".breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            "description": response.css(
                "meta[name=description]::attr(content)"
            ).get(),
            "upc": response.css('th:contains("UPC") + td::text').get(),
        }

        yield book_info

    @staticmethod
    def _get_book_url(response: Response, book: Selector) -> str:
        detailed_book_url = response.urljoin(
            book.css("h3 a::attr(href)").get()
        )
        return detailed_book_url
