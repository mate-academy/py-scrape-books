from typing import Generator

import scrapy

from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, *args, **kwargs) -> Generator[dict]:
        shiftdic = {
            "Zero": 0,
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        for product in response.css("ol.row li"):
            title = product.css("h3 a::attr(title)").get()
            price = product.css(".price_color::text").get().replace("£", "")
            rating = shiftdic[
                product.css(".star-rating::attr(class)").get().split()[-1]
            ]

            product_url = product.css("h3 a::attr(href)").get()
            yield response.follow(
                product_url,
                callback=self.parse_detail,
                meta={
                    "title": title,
                    "price": price,
                    "rating": rating
                }
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_detail(self, response: Response) -> Generator[dict]:
        title = response.meta["title"]
        price = float(response.meta["price"])
        rating = int(response.meta["rating"])

        stock_text = response.css(
            ".product_main .instock.availability::text"
        ).getall()
        stock = int("".join([i for i in str(stock_text).strip() if i.isdigit()]))
        category = str(response.css(".breadcrumb a::text").getall()[-1])
        description = response.css(
            "#product_description ~ p::text"
        ).get(default="").strip()
        upc = response.css(".table.table-striped tr td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc
        }
