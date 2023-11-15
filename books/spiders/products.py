import scrapy

from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    _numbers = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            if book.css("h3 > a::attr(href)").get():
                yield response.follow(
                    book.css("h3 > a::attr(href)").get(), self._parse_book
                )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    def _parse_book(self, response: Response) -> None:
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": self.get_price(response),
            "amount_in_stock": self.get_amount_in_stock(response),
            "rating": self._numbers.get(self.get_rating(response), None),
            "category": response.css(".breadcrumb > li > a::text")
            .getall()[-1],
            "description": response.css("#product_description + p::text")
            .get(),
            "upc": response.css(".table > tr > td::text").getall()[0],
        }

    @staticmethod
    def get_price(response: Response) -> float:
        count = response.css(".product_main .price_color::text").get()
        return float(count.replace("£", "")) if count else 0.0

    @staticmethod
    def get_amount_in_stock(response: Response) -> int:
        amount = response.css(".instock.availability::text").re_first(r"\d+")
        return int(amount) if amount else 0

    @staticmethod
    def get_rating(response: Response) -> str | int:
        rating_str = response.css("p.star-rating::attr(class)").re_first(
            r"star-rating (\w+)"
        )
        return rating_str if rating_str else 0
