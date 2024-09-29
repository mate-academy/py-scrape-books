import re

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):

            detail_page_url = book.css("h3 a::attr(href)").get()

            if detail_page_url:
                detail_page_url = response.urljoin(detail_page_url)
                yield scrapy.Request(detail_page_url, callback=self.book_parse)

        next_page = response.css(".pager > li.next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: Response) -> None:
        title = response.css("div.product_main h1::text").get()

        price = float(
            response.css("p.price_color::text").get().replace("£", "")
        )

        list_amount_in_stock = response.css("p.availability::text").getall()
        text_amount_in_stock = " ".join(list_amount_in_stock).strip()
        match = re.search(r"\((\d+)\s+available\)", text_amount_in_stock)

        if match:
            amount_in_stock = int(match.group(1))

        rating_mapping = {
            "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
        }
        str_rating = response.css(
            "p.star-rating::attr(class)"
        ).get().split()[-1]
        rating = rating_mapping.get(str_rating)

        category = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get().strip()

        description = response.css(
            "div#product_description + p"
        ).css("::text").get()

        upc = response.css(
            "table.table.table-striped tr:contains('UPC') td::text"
        ).get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
