from typing import Generator, Iterator
from urllib.parse import urljoin

import scrapy
from scrapy.http import Response

from ..items import BookscraperItem


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response) -> Iterator[scrapy.Request]:
        category_links = response.css(
            "div.side_categories ul.nav-list > li > ul > li > a"
        )
        yield from response.follow_all(category_links, self.parse_category)

    def parse_category(
            self, response: Response
    ) -> Generator[scrapy.Request, None, None]:
        category = response.css("div.page-header h1::text").get().strip()

        book_links = response.css("article.product_pod h3 a")
        for link in book_links:
            yield response.follow(
                link, self.parse_book, meta={"category": category}
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            next_url = urljoin(response.url, next_page)
            yield scrapy.Request(next_url, self.parse_category)

    def parse_book(
            self,
            response: Response
    ) -> Generator[BookscraperItem, None, None]:
        book = BookscraperItem()

        book["title"] = response.css("div.product_main h1::text").get().strip()
        book["price"] = response.css("p.price_color::text").get().strip()

        stock_text = response.css("p.availability::text").getall()
        stock_text = "".join([s.strip() for s in stock_text])
        if "In stock" in stock_text:
            import re
            stock_match = re.search(r"\((\d+) available\)", stock_text)
            if stock_match:
                book["amount_in_stock"] = int(stock_match.group(1))
            else:
                book["amount_in_stock"] = "In stock"
        else:
            book["amount_in_stock"] = "Out of stock"

        rating_class = response.css("p.star-rating::attr(class)").get()
        if rating_class:
            rating_text = rating_class.split()[1].lower()
            rating_map = {
                "one": 1,
                "two": 2,
                "three": 3,
                "four": 4,
                "five": 5
            }
            book["rating"] = rating_map.get(rating_text, None)

        book["category"] = response.meta.get("category")

        description = response.css("div#product_description + p::text").get()
        book["description"] = (
            description.strip() if description else "No description available"
        )

        product_info_table = response.css("table.table-striped tr")
        for row in product_info_table:
            header = row.css("th::text").get().strip()
            value = row.css("td::text").get().strip()

            if header == "UPC":
                book["upc"] = value

        yield book


custom_settings = {
    "FEED_FORMAT": "jsonlines",
    "FEED_URI": "books.jl"
}
