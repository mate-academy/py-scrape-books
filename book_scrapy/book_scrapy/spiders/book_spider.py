from typing import Generator
import scrapy
from scrapy.http import Response

class QuotesSpider(scrapy.Spider):
    name = "books"
    start_urls = [
        "https://books.toscrape.com/",
    ]

    RATING_MAP = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5,
    }

    def parse(self, response: Response, **kwargs):
        for book_link in response.css(".image_container a::attr(href)").getall():
            full_url = response.urljoin(book_link)
            yield scrapy.Request(full_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response, **kwargs) -> Generator[dict, None, None]:
        quote = response.css(".content")

        rating_class = quote.css(".product_main p.star-rating::attr(class)").get(default='')
        rating_text = rating_class.split()[-1] if rating_class else ''
        rating = self.RATING_MAP.get(rating_text, 0)

        breadcrumb = response.css(".breadcrumb li a::text").getall()
        category = breadcrumb[2] if len(breadcrumb) > 2 else None

        upc_list = quote.css(".table-striped tr td::text").getall()
        upc = upc_list[0] if upc_list else None

        price_text = quote.css(".product_main p.price_color::text").get(default='')
        price = price_text.replace("£", "") if price_text else None

        yield {
            "title": quote.css(".product_main h1::text").get(default=''),
            "price": price,
            "amount_in_stock": quote.css(".product_main p.instock::text").re_first(r"\d+"),
            "rating": rating,
            "category": category,
            "description": quote.css("#product_description + p::text").get(default=''),
            "upc": upc,
        }
