import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, *args, **kwargs) -> None:
        book_urls = response.css(".product_pod h3 a::attr(href)").getall()
        for book_url in book_urls:
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _get_title(response: Response) -> str:
        return response.css("h1::text").get()

    @staticmethod
    def _get_price(response: Response) -> str:
        return response.css(".price_color::text").get()

    @staticmethod
    def _get_amount_in_stock(response: Response) -> str:
        return response.css(".instock.availability::text").re_first(r"\d+")

    @staticmethod
    def _get_rating(response: Response) -> str:
        return response.css(".star-rating").re_first(r"Two|Three|Four|Five|One")

    @staticmethod
    def _get_category(response: Response) -> str:
        return response.css(".breadcrumb li:nth-last-child(2) a::text").get()

    @staticmethod
    def _get_description(response: Response) -> str:
        return response.css("#product_description + p::text").get()

    @staticmethod
    def _get_upc(response: Response) -> str:
        return response.css('.table-striped th:contains("UPC") + td::text').get()

    def parse_book(self, response: Response) -> dict[str, str]:
        yield {
            "title": self._get_title(response),
            "price": self._get_price(response),
            "amount_in_stock": self._get_amount_in_stock(response),
            "rating": self._get_rating(response),
            "category": self._get_category(response),
            "description": self._get_description(response),
            "upc": self._get_upc(response),
        }
