import scrapy
from scrapy.http import Response
from typing import Generator, Any, Dict


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) \
            -> Generator[scrapy.Request, None, None]:
        book_links = response.css("h3 a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book_details)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(
        self, response: Response
    ) -> Generator[Dict[str, Any], None, None]:
        rows = response.css("table.table-striped tr")
        info = {
            row.css("th::text").get(): row.css("td::text").get()
            for row in rows
        }

        rating_map = {
            "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
        }
        raw_rating = (response.css
                      ("p.star-rating::attr(class)").get())
        rating_text = (raw_rating.replace
                       ("star-rating ", "")) if raw_rating else ""

        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css
                           ("p.price_color::text").re_first(r"\d+\.\d+")),
            "amount_in_stock": int(
                response.css("p.instock.availability::text").re_first(r"\d+")
            ),
            "rating": rating_map.get(rating_text, 0),
            "category": response.css(
                "ul.breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": info.get("UPC"),
        }
