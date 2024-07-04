import scrapy
from scrapy.http import Response
from typing import Generator, Optional

RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class AllBooksSpider(scrapy.Spider):
    name = "all_books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(
        self, response: Response, **kwargs
    ) -> Generator[scrapy.Request, None, None]:
        for book in response.css(".product_pod"):
            book_page_url = book.css("h3 > a::attr(href)").get()
            if book_page_url:
                yield response.follow(
                    book_page_url, callback=self.parse_book_detail
                )

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_detail(
            self, response: Response
    ) -> Generator[dict, None, None]:
        yield {
            "title": self.get_title(response),
            "price": self.get_price(response),
            "amount_in_stock": self.get_amount_in_stock(response),
            "rating": self.get_rating(response),
            "category": self.get_category(response),
            "description": self.get_description(response),
            "upc": self.get_upc(response),
        }

    @staticmethod
    def get_title(response: Response) -> Optional[str]:
        title = response.css("div.product_main h1::text").get()
        return title if title else None

    @staticmethod
    def get_price(response: Response) -> Optional[float]:
        price_text = response.css("p.price_color::text").get()
        return float(price_text[1:]) if price_text else None

    @staticmethod
    def get_amount_in_stock(response: Response) -> Optional[int]:
        amount_text = response.css("p.instock.availability::text").re_first(
            r"\((\d+) available\)"
        )
        return int(amount_text) if amount_text else None

    @staticmethod
    def get_rating(response: Response) -> Optional[int]:
        rating_text = response.css("p.star-rating::attr(class)").re_first(
            r"star-rating (\w+)"
        )
        return RATING.get(rating_text) if rating_text else None

    @staticmethod
    def get_category(response: Response) -> Optional[str]:
        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        return category if category else None

    @staticmethod
    def get_description(response: Response) -> Optional[str]:
        description = response.css("div#product_description ~ p::text").get()
        return description if description else None

    @staticmethod
    def get_upc(response: Response) -> Optional[str]:
        upc = response.css(
            "table.table.table-striped tr:nth-child(1) td::text"
        ).get()
        return upc if upc else None
