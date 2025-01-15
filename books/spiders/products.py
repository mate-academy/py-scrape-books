import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from word2number import w2n


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: str)  -> None:
        self.driver.quit()
        super().close(reason)

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css("ol.row > li"):
            detail_info = self._parse_detail_info(response, book)
            rating = book.css("p.star-rating::attr(class)").get()
            rating = w2n.word_to_num(rating.split()[1])
            yield {
                "title": book.css("a::attr(title)").get(),
                "price": book.css(".price_color::text").get().replace("£", ""),
                "amount_in_stock": detail_info.get("amount_in_stock"),
                "rating": rating,
                "category": detail_info.get("category"),
                "description": detail_info.get("description"),
                "upc": detail_info.get("upc"),
            }
        next_page = response.css(".pager > li")[-1].css("a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def _parse_detail_info(self, response: Response, book: Selector) -> dict:
        absolute_url = response.urljoin(book.css("a::attr(href)").get())
        self.driver.get(absolute_url)

        detail_info = {}
        try:
            description_div = self.driver.find_element(
                By.ID, "product_description"
            )
            description = description_div.find_elements(
                By.XPATH, "./following-sibling::p"
            )[0].text[:-7]
        except NoSuchElementException:
            description = "No description"
        detail_info["description"] = description

        category_div = self.driver.find_element(By.CLASS_NAME, "breadcrumb")
        category = category_div.find_elements(By.TAG_NAME, "a")[-1].text
        detail_info["category"] = category

        table = self.driver.find_element(By.TAG_NAME, "table")
        table_lines = table.find_elements(By.TAG_NAME, "tr")
        for line in table_lines:
            th = line.find_element(By.TAG_NAME, "th").text
            if th == "UPC":
                upc = line.find_element(By.TAG_NAME, "td").text
                detail_info["upc"] = upc
            if th == "Availability":
                amount_in_stock_text = line.find_element(
                    By.TAG_NAME, "td"
                ).text
                amount_in_stock = int(
                    "".join(
                        [
                            char
                            for char in amount_in_stock_text
                            if char.isdigit()
                        ]
                    )
                )
                detail_info["amount_in_stock"] = amount_in_stock

        return detail_info
