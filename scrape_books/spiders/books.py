from typing import Dict, Any

import scrapy
from scrapy.http import Response

RATING = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> str:
        for book in response.css("article.product_pod"):
            book_detail_url = response.urljoin(
                book.css("h3 a::attr(href)"
                         ).get())
            yield response.follow(
                book_detail_url,
                callback=self._parse_book_detail
            )

        next_page_url = response.css("li.next a::attr(href)").get()

        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse)

    def _parse_book_detail(self, response: Response) -> Dict[str, Any]:
        yield {
            "title": self._parse_title(response),
            "price": self._parse_price(response),
            "amount_in_stock": self._parse_amount_in_stock(response),
            "rating": self._parse_rating(response),
            "category": self._parse_category(response),
            "description": self._parse_description(response),
            "upc": self._parse_upc(response),
        }

    @staticmethod
    def _parse_title(response: Response) -> str:
        return response.css("h1::text").get()

    @staticmethod
    def _parse_price(response: Response) -> float:
        price_text = response.css("p.price_color::text").get()
        return float(price_text.replace("£", ""))

    @staticmethod
    def _parse_amount_in_stock(response: Response) -> int:
        stock_text = response.css("p.instock.availability::text").getall()
        stock_text = [s.strip() for s in stock_text if s.strip()]
        # Assuming the stock amount is the third word in the filtered list
        stock_amount = stock_text[0].split()[2]
        if stock_amount.isdigit():
            return int(stock_amount)
        else:
            return 0  # or handle this case appropriately

    @staticmethod
    def _parse_rating(response: Response) -> int:
        rating_class = response.css(
            "p.star-rating::attr(class)"
        ).get().split()[-1]
        return RATING[rating_class]

    @staticmethod
    def _parse_category(response: Response) -> str:
        return response.css("ul.breadcrumb li a::text").getall()[-1]

    @staticmethod
    def _parse_description(response: Response) -> str:
        return response.css("div#product_description ~ p::text").get()

    @staticmethod
    def _parse_upc(response: Response) -> str:
        return response.css("table.table tr td::text").get()
