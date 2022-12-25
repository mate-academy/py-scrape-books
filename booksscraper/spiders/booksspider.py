from typing import Generator, Any

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs: Any) -> Generator:
        urls = response.css("h3 > a::attr(href)").extract()

        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url=url, callback=self.parse_details)

        next_page = response.css(".next a::attr(href)").get()

        if next_page is not None:
            next_page = response.urljoin(next_page)

            yield scrapy.Request(next_page, callback=self.parse)

    def parse_details(self, response: Response) -> Generator:
        rating = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        yield {
            "title": response.css("h1::text").get(),
            "price": float(
                response.css(".price_color::text")
                .get()
                .replace("£", "")
            ),
            "amount_in_stock": int(
                response.css(".product_main > p.instock.availability::text")
                .getall()[-1]
                .strip()
                .split()[-2]
                .strip("(")
            ),
            "rating": rating[
                response.css(".star-rating")
                .get()
                .split()[2]
                .replace('">', "")
            ],
            "category": response.css("li > a::text").getall()[-1],
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table-striped")
            .get()
            .split()[4]
            .split("<td>")[-1]
            .replace("</td>", ""),
        }
