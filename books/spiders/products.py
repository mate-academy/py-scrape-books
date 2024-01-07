from typing import Any

import scrapy
from scrapy.http import Response


RATING_MAPPER = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Any:
        for product in response.css(".product_pod"):
            product_url = response.urljoin(
                product.css("h3 > a::attr(href)").get()
            )
            yield scrapy.Request(
                url=product_url,
                callback=self._parse_product_details
            )

        next_page = response.css("li.next a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _parse_product_details(response: Response) -> dict:
        yield {
            "title": response.css("h1::text").get(),
            "price(£)": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                response.css(".instock").get().split()[7][1:]
            ),
            "rating": RATING_MAPPER[
                response.css(".star-rating::attr(class)").get().split()[1]
            ],
            "category": response.css(".breadcrumb li a::text").getall()[2],
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table tr td::text").get(),
        }
