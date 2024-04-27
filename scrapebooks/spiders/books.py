import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        books = response.css("h3 > a::attr(href)").getall()

        for book in books:
            yield response.follow(book, callback=self.parse_book)

        next_page = response.css("ul.pager li.next a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url, callback=self.parse)

    @staticmethod
    def get_stock_amount(string: str) -> int:
        result = ""
        for char in string.strip():
            if char.isdigit():
                result += char
        return int(result)

    @staticmethod
    def get_rating_from_string(string: str) -> int:
        rating = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        return rating[string.split()[-1]]

    def parse_book(self, response: Response) -> dict:
        yield {
            "title": response.css("h1::text").get(),
            "price": float(
                response.css(".price_color::text"
                             ).get().replace("£", "")
            ),
            "remained_in_stock": self.get_stock_amount(
                response.css("td::text")[5].get()
            ),
            "rating": self.get_rating_from_string(
                response.css("p.star-rating::attr(class)").get()
            ),
            "description": response.css(".product_page > p::text").get(),
        }
