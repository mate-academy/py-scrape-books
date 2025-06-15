from typing import Any

import scrapy
from scrapy.http import Response

from scrapybooks.items import ScrapybooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def book_detail(self, response: Response) -> ScrapybooksItem | Any | None:
        title = response.css(".product_main h1::text").get()
        price = response.css(".price_color::text").get().replace("£", "")
        availability_raw = response.css(".instock.availability::text").getall()
        availability = "".join(
            [text.strip()
             for text in availability_raw if text.strip()]
        )
        amount_in_stock = self.extract_in_stock(availability)
        rating_class = response.css(".star-rating").attrib["class"].split()
        rating_str = next(
            (cls for cls in rating_class if cls != "star-rating"),
            "Zero"
        )
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
            "Zero": 0
        }
        rating = rating_map.get(rating_str, 0)
        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        description = (response.css(
            "#product_description ~ p::text")
            .get(default="").strip()
        )
        upc = response.css(
            ".table.table-striped tr:nth-child(1) td::text"
        ).get()

        yield ScrapybooksItem(
            title=title,
            price=float(price),
            amount_in_stock=amount_in_stock,
            rating=rating,
            category=category,
            description=description,
            upc=upc
        )

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            detail_url = response.urljoin(book.css("h3 a::attr(href)").get())
            yield scrapy.Request(detail_url, callback=self.book_detail)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def extract_in_stock(self, availability: str) -> int:
        res = availability[10:]
        result_str = ""
        for one_char in res:
            if one_char.isdigit():
                result_str += one_char
        return int(result_str)
