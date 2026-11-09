import re
import scrapy
from scrapy.http import Response


RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]


    def parse(self, response: Response, **kwargs):
        yield from response.follow_all(
            css="article.product_pod h3 a", callback=self.parse_book
        )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response):
        product = response.css(".product_main")

        yield {
            "title": product.css("h1::text").get(),
            "price": self._parse_price(product.css(".price_color::text").get()),
            "amount_in_stock": self._parse_stock(
                " ".join(product.css(".availability::text").getall())
            ),
            "rating": self._parse_rating(
                product.css(".star-rating::attr(class)").get()
            ),
            "category": response.css(
                ".breadcrumb li:nth-child(3) a::text"
            ).get(),
            "description": response.css(
                "#product_description + p::text"
            ).get(default=""),
            "upc": response.xpath(
                "//th[text()='UPC']/following-sibling::td/text()"
            ).get(),
        }

    @staticmethod
    def _parse_price(price: str) -> float:
        return float(price.replace("£", ""))

    @staticmethod
    def _parse_stock(availability: str) -> int:
        match = re.search(r"\d+", availability)
        return int(match.group()) if match else 0

    @staticmethod
    def _parse_rating(rating_class: str) -> int:
        return RATINGS.get(rating_class.split()[-1], 0)
