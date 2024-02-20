from typing import Any

import scrapy
from scrapy.http import Response

RATING_INTERFACE = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BookSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        books_url = [
            response.urljoin(book_href)
            for book_href in response.css(
                ".product_pod > .image_container > a::attr(href)"
            ).extract()
        ]

        for book_url in books_url:
            yield scrapy.Request(url=book_url, callback=self.parse_single_product)

        next_page = response.css(".pager > .next > a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_single_product(self, response: Response) -> dict[str, [str, int, float]]:
        title = response.css(".product_main > h1::text").get()
        price = float(response.css("p.price_color::text").get().replace("£", ""))

        availability = (
            response.xpath(
                "//th[contains(text(), 'Availability')]/following-sibling::td/text()"
            )
            .get()
            .split("(")[-1]
        )

        amount_in_stock = int(availability.split()[0])

        rating = response.css(".star-rating::attr(class)").get().split()[-1]

        category = response.xpath(
            '//ul[@class="breadcrumb"]/li/a[contains(text(), "Books")]/following::li[1]/a/text()'
        ).get()

        description = response.xpath(
            '//div[@id="product_description"]/following-sibling::p/text()'
        ).get()

        upc = response.xpath(
            '//th[contains(text(), "UPC")]/following-sibling::td/text()'
        ).get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": RATING_INTERFACE.get(rating, rating),
            "category": category,
            "description": description,
            "upc": upc,
        }
