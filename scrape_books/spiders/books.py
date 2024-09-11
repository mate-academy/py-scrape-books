from typing import Any, Generator
import re
import scrapy
from scrapy.http import Response
from scrape_books.items import Book


RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(
            self, response: Response, **kwargs: Any
    ) -> Generator[scrapy.Request, None, None]:
        book_links = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()
        for link in book_links:
            absolute_url = response.urljoin(link)
            yield scrapy.Request(url=absolute_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield scrapy.Request(
                url=response.urljoin(next_page), callback=self.parse
            )

    def parse_book(self, response: Response) -> Generator[Book]:
        book = Book(
            title=response.css("div.product_main h1::text").get(),
            price=self.extract_price(
                response.css("p.price_color::text").get()
            ),
            amount_in_stock=self.extract_availability(response),
            rating=self.extract_rating(response),
            category=response.css(
                "ul.breadcrumb li:nth-child(3) a::text"
            ).get(),
            description=self.extract_description(response),
            upc=self.extract_upc(response),
        )
        yield book

    def extract_price(self, price_str: str) -> float:
        try:
            return float(price_str
                         .replace("£", "")
                         .replace(",", ""))
        except ValueError:
            return 0.0

    def extract_availability(self, response: Response) -> int:
        availability_text = response.css("p.availability::text").getall()
        availability_str = "".join(availability_text).strip()
        return self.extract_number(availability_str)

    def extract_number(self, text: str) -> int:
        number = re.findall(r"\d+", text)
        return int("".join(number)) if number else 0

    def extract_rating(self, response: Response) -> int:
        star_classes = response.css("p.star-rating::attr(class)").get()
        if star_classes:
            match = re.search(r"star-rating (\w+)", star_classes)
            if match:
                rating = match.group(1)
                return RATING_MAP.get(rating, 0)
        return 0

    def extract_description(self, response: Response) -> str:
        description = response.css(
            "meta[name='description']::attr(content)"
        ).get()
        return description.strip() if description else ""

    def extract_upc(self, response: Response) -> str:
        upc = (response.css("tr td::text").getall())[0]
        return upc.strip() if upc else ""
