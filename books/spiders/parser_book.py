import re
from typing import Any

import scrapy
from scrapy import Request
from scrapy.http import Response
from selenium import webdriver


class ParserBookSpider(scrapy.Spider):
    name = "parser_book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: str) -> Any:
        self.driver.close()

    def parse(self, response: Response, **kwargs) -> None:

        for product in response.css(".product_pod"):
            rating_word = product.css("p.star-rating::attr(class)").re_first(
                r"star-rating (\w+)"
            )
            rating = self.rating_map.get(rating_word, 0)
            title = product.css("h3 a::attr(title)").get()
            price = float(
                product.css(".price_color::text").get().replace("£", "")
            )

            abs_url = response.urljoin(product.css("h3 a::attr(href)").get())
            yield Request(
                abs_url,
                callback=self.detail_info,
                meta={"title": title, "price": price, "rating": rating},
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def detail_info(self, response: Response) -> None:

        self.driver.get(response.url)
        category = self.driver.find_element(
            "css selector", ".breadcrumb li:nth-child(3) a"
        ).text
        description = self.driver.find_element(
            "css selector", "#product_description + p"
        ).text
        upc = self.driver.find_element(
            "xpath", "//th[text()='UPC']/following-sibling::td"
        ).text
        availability_text = self.driver.find_element(
            "xpath", "//th[text()='Availability']/following-sibling::td"
        ).text

        amount = 0
        match = re.search(r"\((\d+)\s+available\)", availability_text)
        if match:
            amount = int(match.group(1))
        yield {
            "title": response.meta["title"],
            "price": response.meta["price"],
            "rating": response.meta["rating"],
            "amount_in_stock": amount,
            "category": category,
            "description": description,
            "upc": upc,
        }
