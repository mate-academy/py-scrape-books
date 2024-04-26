from typing import Any

import requests
import scrapy
from bs4 import BeautifulSoup
from scrapy import Selector
from scrapy.http import Response

from topscrape.services import convert_to_int


class BooksSpider(scrapy.Spider):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.page = None

    name = "books"

    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> dict:
        for url in response.css(
                ".product_pod > h3 > a::attr(href)"
        ).getall():

            detail_page_url = response.urljoin(url)

            self.page = self._get_detail_page(detail_page_url)

            title = self._get_title()
            price = self._get_price()
            amount_in_stock = self._get_amount_in_stock()
            rating = self._get_rating()
            category = self._get_rating()
            description = self._get_description()
            upc = self._get_upc()

            yield {
                "Title": title,
                "Price": price,
                "Amount_in_stock": amount_in_stock,
                "Rating": convert_to_int(rating),
                "Category": category,
                "Description": description,
                "UPC": upc,
            }

        next_page = response.css("li.next > a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _get_title(self) -> str:
        return self.page.css("div.col-sm-6.product_main > h1::text").get()

    def _get_price(self) -> float:
        return float(self.page.css(".price_color::text").get()[2:])

    def _get_amount_in_stock(self) -> str:
        return self.page.css(
            "p.instock.availability"
        ).xpath("string()").get().strip()

    def _get_rating(self) -> str:
        _, rating = self.page.css("p.star-rating::attr(class)").get().split()
        return rating

    def _get_category(self) -> str:
        return self.page.xpath(
            "//th[text()='Product Type']/following-sibling::td/text()"
        ).get()

    def _get_description(self) -> str:
        return self.page.css("article.product_page > p::text").get()

    def _get_upc(self) -> str:
        return self.page.xpath(
            "//th[text()='UPC']/following-sibling::td/text()"
        ).get()

    @staticmethod
    def _get_detail_page(url: str) -> Selector | None:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            return Selector(text=str(soup))
