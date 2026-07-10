import scrapy
from scrapy.http import Response


RATINGS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}

MAX_BOOKS = 1000


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    custom_settings = {
        "FEEDS": {
            "books.jl": {
                "format": "jsonlines",
                "overwrite": True,
            },
        },
    }

    books_scraped = 0

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            if self.books_scraped >= MAX_BOOKS:
                return

            detail_url = book.css("h3 a::attr(href)").get()
            yield response.follow(detail_url, callback=self.parse_book)

        if self.books_scraped < MAX_BOOKS:
            next_page = response.css("li.next a::attr(href)").get()
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> None:
        if self.books_scraped >= MAX_BOOKS:
            return

        self.books_scraped += 1

        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": self.get_price(response),
            "amount_in_stock": self.get_amount_in_stock(response),
            "rating": self.get_rating(response),
            "category": self.get_category(response),
            "description": self.get_description(response),
            "upc": self.get_upc(response),
        }

    @staticmethod
    def get_price(response: Response) -> float:
        price = response.css(".price_color::text").get()
        return float(price.replace("£", ""))

    @staticmethod
    def get_amount_in_stock(response: Response) -> int:
        rows = response.css(".table tr")
        for row in rows:
            header = row.css("th::text").get()
            if header == "Availability":
                value = row.css("td::text").get()
                digits = "".join(ch for ch in value if ch.isdigit())
                return int(digits) if digits else 0
        return 0

    @staticmethod
    def get_rating(response: Response) -> int:
        rating_class = response.css(".star-rating::attr(class)").get()
        word = rating_class.replace("star-rating", "").strip()
        return RATINGS.get(word, 0)

    @staticmethod
    def get_category(response: Response) -> str:
        return response.css(".breadcrumb li a::text").getall()[-1]

    @staticmethod
    def get_description(response: Response) -> str:
        description = response.css("#product_description + p::text").get()
        return description.strip() if description else ""

    @staticmethod
    def get_upc(response: Response) -> str:
        return response.css(".table td::text").get()
