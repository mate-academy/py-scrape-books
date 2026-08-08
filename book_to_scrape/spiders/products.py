from typing import Any, Generator
import re
import scrapy
from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) -> Generator[Any, None, None]:

        for product in response.css(".product_pod"):
            book_url = product.css("h3 a::attr(href)").get()

            title = product.css("::attr(title)").get()
            price = product.css(".price_color::text").get().replace("£", "")
            rating = product.css(
                ".star-rating::attr(class)"
            ).get().split(" ")[1]
            yield response.follow(
                book_url,
                self._parse_book,
                meta={
                    "title": title,
                    "price": price,
                    "rating": rating
                },
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def _parse_book(self, response: Response) -> Any:
        title = response.meta["title"]
        price = response.meta["price"]
        rating = response.meta["rating"]

        description = response.css("#product_description + p::text").get()
        category = response.css(".breadcrumb li a::text").getall()[2]

        availability = " ".join(
            t.strip() for t in response.css(
                "p.instock.availability::text"
            ).getall()
        )

        amount = int(re.search(r"\d+", availability).group())

        upc = response.xpath(
            '//th[text()="UPC"]/following-sibling::td/text()'
        ).get()

        yield {
            "title": title,
            "price": price,
            "rating": rating,
            "description": description,
            "category": category,
            "amount_in_stock": amount,
            "upc": upc
        }
