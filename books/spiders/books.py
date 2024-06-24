import scrapy
from scrapy.http import Response

NUM_DICT = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: Response, **kwargs) -> Response:
        book_links = response.css("article > h3 > a")
        for book_link in book_links:
            yield response.follow(book_link, callback=self.parse_book)

        next_page = response.css("ul.pager > li.next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> dict:
        return {
            "title": self._get_title(response),
            "price": self._get_price(response),
            "amount_in_stock": self._get_amount_in_stock(response),
            "rating": self._get_rating(response),
            "category": self._get_category(response),
            "description": self._get_description(response),
            "upc": self._get_upc(response),
        }

    def _get_title(self, response: Response) -> str:
        return response.css(".product_main > h1::text").get()

    def _get_price(self, response: Response) -> float:
        return float(response.css(".price_color::text").get().replace("£", ""))

    def _get_amount_in_stock(self, response: Response) -> int:
        info_table = response.css(".table td::text").getall()
        return int("".join(char for char in info_table[5] if char.isnumeric()))

    def _get_rating(self, response: Response) -> int:
        return NUM_DICT[response.css(".star-rating::attr(class)").get().split()[1]]

    def _get_category(self, response: Response) -> str:
        return response.css("ul.breadcrumb > li > a::text").getall()[-1]

    def _get_description(self, response: Response) -> str:
        return response.css(".product_page > p::text").get()

    def _get_upc(self, response: Response) -> str:
        info_table = response.css(".table td::text").getall()
        return info_table[0]
