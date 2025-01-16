import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]
    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            rating_class = book.css(
                ".star-rating::attr(class)"
            ).get().split()[-1]

            yield response.follow(
                book.css("h3 a::attr(href)").get(),
                callback=self.parse_book_details,
                meta={
                    "title": book.css("h3 a::attr(title)").get(),
                    "price": float(
                        book.css(
                            ".product_price .price_color::text"
                        ).get().replace("£", "")
                    ),
                    "rating": self.rating_map.get(rating_class, 0)
                }
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(self, response: Response) -> None:
        try:
            amount_in_stock = int(
                response.css("th:contains('Availability') + td::text")
                .get()
                .split("(")[-1]
                .split(" ")[0]
            )
        except (AttributeError, IndexError, ValueError):
            amount_in_stock = 0

        yield {
            "title": response.meta["title"],
            "price": response.meta["price"],
            "amount_in_stock": amount_in_stock,
            "rating": response.meta["rating"],
            "description": response.css(
                "#product_description + p::text").get(),
            "upc": response.css("th:contains('UPC') + td::text").get(
                default="No description available"
            )
        }
