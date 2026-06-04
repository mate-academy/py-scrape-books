from typing import Any, Generator

import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(options=options)

    def close(self, reason: str) -> None:
        self.driver.quit()

    def parse(
        self,
        response: Response,
        **kwargs,
    ) -> Generator[dict[str, str | float], Any, None]:
        for book in response.css(".product_pod"):
            parse_detail = self._parse_detail_info(response, book)
            yield {
                "title": str(book.css("h3 a::attr(title)").get()),
                "price": float(
                    book.css(".price_color::text").get().replace("£", "")
                ),
                "amount_in_stock": parse_detail["in_stock"],
                "rating": parse_detail["rating"],
                "category": parse_detail["category"],
                "description": parse_detail["description"],
                "upc": parse_detail["upc"],
            }

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_detail_info(self, response: Response, book: Selector) -> str:
        rating_map = {
            "Zero": 0,
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }

        absolute_url = response.urljoin(book.css("h3 a::attr(href)").get())
        self.driver.get(absolute_url)

        in_stock_element = self.driver.find_element(
            By.CSS_SELECTOR, ".instock.availability"
        )
        update_in_stock = in_stock_element.text.replace(
            "In stock (", ""
        ).replace(
            " available)", ""
        )

        raw_rating_class = book.css(".star-rating::attr(class)").get()
        rating_word = raw_rating_class.split()[-1] \
            if raw_rating_class else "Zero"
        rating_number = rating_map.get(rating_word, 0)

        category_element = self.driver.find_element(
            By.CSS_SELECTOR, ".breadcrumb li:nth-last-child(2) a"
        ).text

        description_element = self.driver.find_element(
            By.CSS_SELECTOR, "#product_description + p"
        ).text

        upc_element = self.driver.find_element(
            By.CSS_SELECTOR, ".table tr:nth-child(1) td"
        ).text

        result = {
            "in_stock": update_in_stock,
            "rating": rating_number,
            "category": category_element,
            "description": description_element,
            "upc": upc_element,
        }

        return result
