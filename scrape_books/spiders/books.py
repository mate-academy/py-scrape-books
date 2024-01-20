import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    rating_to_num = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(self, response: Response, **kwargs) -> dict:
        book_page_links = response.css("h3 > a::attr(href)")
        yield from response.follow_all(book_page_links, self.parse_book)

        pagination_links = response.css("li.next a")
        yield from response.follow_all(pagination_links, self.parse)

    @staticmethod
    def parse_book(response: Response) -> dict:
        yield {
            "title": response.css("h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                response.css(
                    "tr:contains('Availability') td::text"
                ).get().split()[2].replace("(", "")
            ),
            "rating": BooksSpider.rating_to_num[
                response.css(".star-rating::attr(class)").get().split()[1]
            ],
            "category": response.css(".breadcrumb > li > a::text").getall()[2],
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": response.css(
                "tr:contains('UPC') td::text"
            ).get()
        }
