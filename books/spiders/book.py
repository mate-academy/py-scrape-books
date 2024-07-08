import scrapy
from scrapy.http import Response

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_url = book.css("h3 > a::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_book_detail)

        next_page_url = response.css(".next > a::attr(href)").get()

        if next_page_url is not None:
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book_detail(self, response: Response):
        yield {
            "title": self.get_title(response),
            "price": self.get_price(response),
            "amount_in_stock": self.get_amount_in_stock(response),
            "rating": self.get_rating(response),
            "category": self.get_category(response),
            "description": self.get_description(response),
            "upc": self.get_upc(response)
        }

    @staticmethod
    def get_title(response: Response) -> str:
        return response.css("h1::text").get()

    @staticmethod
    def get_price(response: Response) -> float:
        price_str = response.css(".price_color::text").get().replace("£", "")
        return float(price_str)

    @staticmethod
    def get_amount_in_stock(response: Response) -> int:
        return int(response.css(".availability::text").re_first(r'\d+'))

    @staticmethod
    def get_rating(response: Response) -> int:
        rating_class = response.css(".star-rating::attr(class)").get().split()[-1]
        return RATING_MAP.get(rating_class, 0)

    @staticmethod
    def get_category(response: Response) -> str:
        return response.css(".breadcrumb > li > a::text").getall()[-1]

    @staticmethod
    def get_description(response: Response) -> str:
        return response.css(".product_page > p::text").get()

    @staticmethod
    def get_upc(response: Response) -> str:
        return response.css(".table > tr").css("td::text").get()
