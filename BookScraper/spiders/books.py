import re
import scrapy

from scrapy.http import Response

from BookScraper.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            detail_url = book.css("div.image_container > a::attr(href)").get()

            yield scrapy.Request(
                url=response.urljoin(detail_url),
                callback=self.parse_detail
            )

        next_page = response.css("ul.pager > li.next > a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def get_stock_amount(response: Response) -> int:
        availability = response.css("p.instock.availability").get()
        amount_str = re.search(r"\d+", availability).group()
        return int(amount_str) if amount_str else 0

    @staticmethod
    def get_literal_rating_to_int(response: Response) -> int | str:
        ratings = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        rating_str = response.css(
            "p.star-rating::attr(class)"
        ).get().split()[1]

        return ratings.get(rating_str, "No data")

    def parse_detail(self, response: Response) -> BookItem:
        yield BookItem(
            title=response.css("div.product_main > h1::text").get(),
            price=float(response.css(".price_color::text").get()[1:]),
            amount_in_stock=self.get_stock_amount(response),
            rating=self.get_literal_rating_to_int(response),
            category=response.css(
                "ul.breadcrumb li:nth-last-child(2) > a::text"
            ).get(),
            description=response.css(
                "div#product_description + p::text"
            ).get(),
            upc=response.css(".table th:contains('UPC') + td::text").get()
        )
