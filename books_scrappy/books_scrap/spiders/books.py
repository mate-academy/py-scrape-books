import re
import scrapy
from typing import Generator
from scrapy.http import Response
from books_scrappy.books_scrap.items import ParseBooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def __init__(self, last_page: int = 1, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.last_page = int(last_page)

    def start_requests(self) -> Generator:
        headers = {"User-Agent": "Mozilla/5.0"}
        for i in range(1, self.last_page + 1):
            if i == 1:
                url = self.start_urls[0]
            else:
                url = f"https://books.toscrape.com/catalogue/page-{i}.html"
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def parse(self, response: Response) -> Generator:
        for href in response.css("h3 a::attr(href)").getall():
            self.log(f"url: {href}")
            yield response.follow(href, callback=self.parse_book_detail)

        next_page = response.css("div ul.pager li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_detail(self, response: Response) -> Generator:
        stars = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

        item = ParseBooksItem()
        item["title"] = response.css("div.product_main h1::text").get()

        price_raw = response.css("div.product_main p.price_color::text").get()
        item["price"] = price_raw[1:] if price_raw else None

        amount_raw = "".join(
            response.css("div.product_main p.instock.availability::text").getall()
        ).strip()
        match = re.search(r"(\d+) available", amount_raw)
        item["amount_in_stock"] = match.group(1) if match else None

        rating_class = response.css("div.product_main p.star-rating").attrib.get(
            "class", ""
        )
        rating = rating_class.split()[-1] if rating_class else ""
        item["rating"] = stars.get(rating)

        categories = response.css("ul.breadcrumb li a::text").getall()
        item["category"] = categories[-2] if len(categories) >= 2 else None

        item["description"] = response.css("#product_description ~ p::text").get()

        table_headers = response.css("table.table-striped th::text").getall()
        table_content = response.css("table.table-striped td::text").getall()
        for name, value in zip(table_headers, table_content):
            if name == "UPC":
                item["upc"] = value
                break

        yield item
