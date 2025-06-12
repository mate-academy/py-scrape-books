import scrapy


from typing import Generator

import scrapy
from scrapy.http import Response

from book_scrapy.items import ParseBooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def __init__(self, last_page: int=1, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.last_page = last_page

    def start_requests(self) -> Generator:
        base_url = "https://books.toscrape.com/catalogue/page-{page}.html"
        headers = {"User-Agent": "Mozilla/5.0"}
        for i in range(1, self.last_page + 1):
            url = base_url.format(page=i)
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def parse_book_detail(self, response: Response) -> Generator:
        stars = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        item = ParseBooksItem()
        item["title"] = response.css("div.product_main h1::text").get()
        item["price"] = response.css("div.product_main p.price_color::text").get()[1:]
        import re
        amount_raw = ''.join(response.css("div.product_main p.instock.availability::text").getall()).strip()
        match = re.search(r'(\d+) available', amount_raw)
        item["amount_in_stock"] = match.group(1) if match else None
        rating = response.css(
            "div.product_main p.star-rating::attr(class)"
        ).get().split()[-1]
        item["rating"] = stars[rating]

        # Категорія - передостанній елемент breadcrumb
        item["category"] = response.css("ul.breadcrumb li a::text").getall()[-2]
        # Опис - після #product_description
        item["description"] = response.css("#product_description ~ p::text").get()
        table_headers = response.css("table.table-striped th::text").getall()
        table_content = response.css("table.table-striped td::text").getall()
        for name, value in zip(table_headers, table_content):
            if name == "UPC":
                item["upc"] = value
                break
        yield item

    def parse(self, response: Response) -> Generator:
        for href in response.css("h3 a::attr(href)").getall():
            self.log(f"url: {href}")
            yield response.follow(href, self.parse_book_detail)

        # next page:
        next_page = response.css("div ul.pager li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
