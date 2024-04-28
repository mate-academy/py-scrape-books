import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        book_links = response.css("h3 > a::attr(href)").getall()

        for book_link in book_links:
            yield response.follow(book_link, callback=self.parse_book)

        next_page_link = response.css("ul.pager li.next a::attr(href)").get()
        if next_page_link:
            next_page_url = response.urljoin(next_page_link)
            yield response.follow(next_page_url, callback=self.parse)

    def extract_stock_amount(self, string: str) -> int:
        digits = "".join(filter(str.isdigit, string.strip()))
        return int(digits)

    def extract_rating(self, string: str) -> int:
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        return rating_map[string.split()[-1]]

    def parse_book(self, response: Response) -> dict:
        yield {
            "title": response.css("h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": self.extract_stock_amount(
                response.css("td::text")[5].get()
            ),
            "rating": self.extract_rating(
                response.css("p.star-rating::attr(class)").get()
            ),
            "description": response.css(".product_page > p::text").get(),
        }
