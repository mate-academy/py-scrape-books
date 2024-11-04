import re
import scrapy
from scrapy.http import Response


class BookParseSpider(scrapy.Spider):
    name = "book_parse"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> scrapy.Request:
        for book in response.css(".product_pod"):
            detail_page = book.css("h3 a::attr(href)").get()
            yield response.follow(detail_page, self.parse_book)

        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response: Response) -> dict:
        title = response.css(".product_main h1::text").get()
        price = float(
            response.css(".price_color::text").get().replace("£", "").strip()
        )
        availability_text = response.css(
            "p.instock.availability::text"
        ).getall()
        combined_text = " ".join(
            text.strip() for text in availability_text if text.strip()
        )
        amount_in_stock = (
            re.search(r"\d+", combined_text).group() if combined_text else "0"
        )
        rating_class = response.css("p.star-rating::attr(class)").get()
        rating = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}.get(
            rating_class.replace("star-rating ", ""), 0
        )

        category = response.css(".breadcrumb li:nth-child(3) a::text").get()
        description = response.css("#product_description + p::text").get(
            default="No description available."
        )
        upc = response.css(".table-striped td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
