import re

import scrapy
from scrapy.http import Response
from typing import Dict, Any, Generator
from library.items import LibraryItem

rating_map = {
    "Zero": 0,
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Generator:
        for product in response.css("article.product_pod"):
            link = product.css("h3 a::attr(href)").get()
            yield response.follow(link, callback=self.parse_product)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_product(
            self,
            response: Response
    ) -> Generator[Dict[str, Any], None, None]:
        item = LibraryItem()
        rating_class = response.css("p.star-rating::attr(class)").get()
        rating_text = rating_class.split()[-1] if rating_class else None

        stock_text = "".join(
            response.css("p.instock.availability::text").getall()
        )
        match = re.search(r"\d+", stock_text)
        amount = int(match.group()) if match else 0

        description = response.xpath(
            "//div[@id='product_description']/following-sibling::p/text()"
        ).get()

        price_raw = response.css(".price_color::text").get()
        price = float(price_raw.replace("£", "")) if price_raw else None

        item["title"] = response.css("h1::text").get()
        item["price"] = price
        item["amount_in_stock"] = amount
        item["rating"] = rating_map.get(rating_text)
        item["category"] = response.xpath(
            "//ul[@class='breadcrumb']/li[last()-1]/a/text()"
        ).get()
        item["description"] = description
        item["upc"] = response.css("table tr:nth-child(1) td::text").get()

        yield item
