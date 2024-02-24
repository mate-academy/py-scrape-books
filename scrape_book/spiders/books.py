import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Response:
        for book_url in response.css(".product_pod h3 a::attr(href)").getall():
            yield scrapy.Request(
                response.urljoin(book_url), callback=self.parse_detail
            )

        next_page = response.css(".pager .next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_detail(self, response: Response) -> dict:
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": response.css(".instock")
            .get()
            .split()[-3]
            .replace("(", ""),
            "rating": self.get_rating(
                response.css("p.star-rating::attr(class)").get().split()[-1]
            ),
            "category": response.css(".breadcrumb li a::text").getall()[-1],
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": response.css(".table-striped td::text").get(),
        }

    @staticmethod
    def get_rating(written_number: str) -> int:
        number = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        return number.get(written_number)
