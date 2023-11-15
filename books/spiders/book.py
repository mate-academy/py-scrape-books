import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield scrapy.Request(
                    response.urljoin(book_url), callback=self.parse_book
            )

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def check_stock_status(response):
        return "In Stock" if response.css(".icon-ok") else "Out of Stock"

    @staticmethod
    def get_rating(response: Response) -> int:
        rating = response.css(".star-rating::attr(class)").get().split(" ")[1]

        numeric_ratings = {
            "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
        }

        return numeric_ratings.get(rating)

    def parse_book(self, response: Response) -> None:
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": response.css(".price_color::text").get().replace("£", ""),
            "amount_in_stock": self.check_stock_status(response),
            "rating": self.get_rating(response),
            "category": response.css(
                ".breadcrumb > li:nth-child(3) a::text"
            ).get(),
            "description": response.css(
                ".product_page > p::text"
            ).get(),
            "upc": response.css(
                ".table-striped tr:nth-child(1) td::text"
            ).get(),
        }
