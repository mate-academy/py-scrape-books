import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) -> Response:
        for book_url in response.css(
                "article.product_pod h3 a::attr(href)"
        ).getall():
            yield response.follow(book_url, callback=self.parse_book)
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> dict:
        yield {
            "title": self.extract_with_css(
                response, "div.product_main h1::text"
            ),
            "price": self.extract_with_css(
                response, "p.price_color::text"
            ),
            "amount_in_stock": self.extract_amount_in_stock(
                response
            ),
            "rating": self.extract_rating(
                response
            ),
            "category": self.extract_with_css(
                response, "ul.breadcrumb li.active::text"
            ),
            "description": self.extract_with_css(
                response, ".product_page > p::text"
            ),
            "upc": self.extract_with_css(
                response, "table.table.table-striped tr td::text"
            ),
        }

    def extract_with_css(self, response: Response, query: str) -> str:
        return str(response.css(query).get(default="").strip())

    def extract_amount_in_stock(self, response: Response) -> int:
        availability_text = self.extract_with_css(
            response, "p.instock.availability"
        )
        amount_in_stock = int(
            "".join(filter(str.isdigit, availability_text))
        )
        return amount_in_stock

    def extract_rating(self, response: Response) -> int:
        classes = response.css(
            "p.star-rating::attr(class)"
        ).get().split()
        rating = classes[-1] if len(classes) > 1 else 0
        return rating
