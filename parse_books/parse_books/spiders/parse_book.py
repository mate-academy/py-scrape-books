import scrapy
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class Driver:
    def __init__(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def closed(self) -> None:
        self.driver.quit()


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def close(self, reason) -> None:
        self.driver.close()

    def parse(self, response: Response, **kwargs):
        for book in response.css("div > ol > li"):
            detail_url = response.urljoin(
                book.css("article > h3 > a::attr(href)").get()
            )
            self.driver.get(detail_url)

            description_element = self.driver.find_elements(
                By.CSS_SELECTOR, "div > article > p"
            )
            description = description_element[0].text if description_element else None

            yield {
                "title": self.extract_text(
                    By.CSS_SELECTOR, "div > article > div.row > div.product_main > h1"
                ),
                "price": self.extract_price(),
                "amount_in_stock": self.extract_amount_in_stock(),
                "rating": self.extract_rating(),
                "category": self.extract_category(),
                "upc": self.extract_text(
                    By.CSS_SELECTOR,
                    "div > article > table.table-striped > tbody > tr > td",
                ),
                "description": description,
            }

        next_page = response.css(".pager > li.next").css("a::attr(href)").get()

        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def extract_text(self, by: By, selector: str) -> str:
        element = self.driver.find_element(by, selector)
        return element.text

    def extract_price(self) -> float:
        price_text = self.extract_text(
            By.CSS_SELECTOR,
            "div > article > div.row > div.product_main > p.price_color",
        )
        return float(price_text.split("£")[1])

    def extract_amount_in_stock(self) -> int:
        amount_in_stock_text = self.extract_text(
            By.CSS_SELECTOR, "div > article > div.row > div.product_main > p.instock"
        )
        return int(amount_in_stock_text.split("(")[1].split(" ")[0])

    def extract_rating(self) -> int:
        rating_element = self.driver.find_elements(
            By.CSS_SELECTOR, "div > article > div.row > div.product_main > p"
        )[2]
        rating_class = rating_element.get_attribute("class").split(" ")[1]
        return RATING.get(rating_class, 0)

    def extract_category(self) -> str:
        category_element = self.driver.find_elements(
            By.CSS_SELECTOR, "div > div.page_inner > ul.breadcrumb > li"
        )[2]
        return category_element.text
