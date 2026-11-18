import scrapy
from scrapy.http import Response

RATING_MAP = {
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

    def parse(self, response: Response, **kwargs):
        """Step 1: collect links to books from a listing page and paginate."""
        yield from response.follow_all(
            response.css("article.product_pod h3 a"),
            callback=self.parse_book,
        )

        next_page = response.css("li.next a")
        if next_page:
            yield response.follow(next_page[0], callback=self.parse)

    def parse_book(self, response: Response):
        """Step 2: parse a single book page."""
        yield {
            "title": response.css("h1::text").get(),
            "price": self._parse_price(response),
            "amount_in_stock": self._parse_amount_in_stock(response),
            "rating": self._parse_rating(response),
            "category": self._parse_category(response),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": self._parse_upc(response),
        }

    @staticmethod
    def _parse_price(response: Response) -> float:
        price = response.css("p.price_color::text").re_first(r"[\d.]+")
        return float(price)

    @staticmethod
    def _parse_amount_in_stock(response: Response) -> int:
        amount = response.css("p.availability").re_first(r"\d+")
        return int(amount) if amount else 0

    @staticmethod
    def _parse_rating(response: Response) -> int:
        classes = response.css("p.star-rating::attr(class)").get()
        word = classes.split()[-1]
        return RATING_MAP[word]

    @staticmethod
    def _parse_category(response: Response) -> str:
        return response.css("ul.breadcrumb li:nth-child(3) a::text").get()

    @staticmethod
    def _parse_upc(response: Response) -> str:
        return response.xpath(
            "//th[text()='UPC']/following-sibling::td/text()"
        ).get()
