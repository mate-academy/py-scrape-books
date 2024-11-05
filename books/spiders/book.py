import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        for product_url in response.css("h3 > a::attr(href)").getall():
            product_url = response.urljoin(product_url)
            yield scrapy.Request(product_url, callback=self.parse_product)

        next_page = response.css("li.next > a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def extract_book_name(self, response: Response) -> str:
        return response.css("h1::text").get()

    def get_price(self, response: Response) -> float:
        price_str = response.css(".price_color::text").get()
        if price_str:
            return float(price_str.replace("£", "").strip())
        return 0.0

    def get_amount_in_stock(self, response: Response) -> int:
        return int(
            response.css(
                ".table.table-striped tr td::text"
            ).getall()[-2].split()[-2].replace("(", "")
        )

    def get_rating(self, response: Response) -> int:
        rating_str = response.css(
            "p.star-rating::attr(class)"
        ).get().split()[-1]
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        return rating_map.get(rating_str, 0)

    def get_category(self, response: Response) -> str:
        return response.css("ul.breadcrumb li:nth-child(3) a::text").get()

    def get_description(self, response: Response) -> str:
        return response.css("#product_description + p::text").get()

    def get_upc(self, response: Response) -> str:
        return response.css(
            ".table-striped th:contains('UPC') + td::text"
        ).get()

    def parse_product(self, response: Response) -> None:
        yield {
            "title": self.extract_book_name(response),
            "price": self.get_price(response),
            "amount": self.get_amount_in_stock(response),
            "rating": self.get_rating(response),
            "category": self.get_category(response),
            "description": self.get_description(response),
            "upc": self.get_upc(response),
        }
