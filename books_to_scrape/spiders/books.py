import scrapy
from scrapy import Request
from scrapy.http import Response

from books_to_scrape.items import BooksToScrapeItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]

    def start_requests(self):
        base_url = "https://books.toscrape.com/"
        headers = {
            "User-Agent":
                "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/51.0.2704.64 Safari/537.36",
            "Referer": "https://www.google.com/"
        }

        first_page = 1
        last_page = 50
        for i in range(first_page, last_page + 1):
            url = base_url + f"/catalogue/page-{i}.html"
            yield scrapy.Request(
                url=url, headers=headers, callback=self.parse
            )

    def parse(self, response: Response, **kwargs) -> Request:
        book_href_list = response.css(
            "article.product_pod > h3 > a::attr(href)"
        ).getall()
        for href in book_href_list:
            yield response.follow(
                href, callback=self._parse_book_detail_info
            )

    def _parse_books(self, response: Response) -> Response:
        book_href_list = response.css(
            "article.product_pod > h3 > a::attr(href)"
        ).getall()
        for href in book_href_list:
            yield response.follow(
                href, callback=self._parse_book_detail_info
            )

    def _parse_book_detail_info(
            self,
            response: Response,
    ) -> BooksToScrapeItem:
        book = BooksToScrapeItem()

        book["title"] = response.css(
            "div.col-sm-6.product_main > h1::text"
        ).get()
        book["price"] = float(response.css(
            ".price_color::text"
        ).get().replace("£", ""))
        book["amount_in_stock"] = int(response.css(
            ".instock.availability::text"
        ).getall()[1].split()[-2][1:])

        book["rating"] = self._get_rating(
            response.css(
                ".star-rating::attr(class)"
            ).get()
        )
        book["category"] = response.css(
            ".breadcrumb > li > a::text"
        ).getall()[-1]
        book["description"] = self._get_description(
            response.css(
                "#content_inner > article > p::text"
            ).getall()
        )
        book["upc"] = response.css(
            "table > tr > td::text"
        ).get()

        return book

    @staticmethod
    def _get_rating(class_name: str) -> int:
        rating_dict = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        return rating_dict[
            class_name.split()[-1]
        ]

    @staticmethod
    def _get_description(descriptions: list[str]) -> str:
        if descriptions:
            return descriptions[0]
        else:
            return "No description"
