import scrapy
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.logger.setLevel(logging.INFO)

    def close(self, reason: str) -> None:
        self.driver.close()

    def parse(self, response: Response, **kwargs) -> dict:
        for book in response.css("article.product_pod"):
            detail_url = response.urljoin(book.css("h3 a::attr(href)").get())
            yield {
                "title": self.parse_title(book),
                "price": self.parse_price(book),
                "amount_in_stock": self.parse_amount_in_stock(detail_url),
                "rating": self.parse_rating(book),
                "category": self.parse_category(detail_url),
                "description": self.parse_description(detail_url),
                "upc": self.parse_upc(detail_url),
            }

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    @staticmethod
    def parse_title(response: Response) -> str:
        return response.css("h3 a::attr(title)").get()

    @staticmethod
    def parse_price(response: Response) -> float:
        return float(
            response.css("p.price_color::text").get().replace("£", "")
        )

    def parse_amount_in_stock(self, detail_url: str) -> int:
        self.driver.get(detail_url)
        try:
            stock_text = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".instock.availability")
                )
            ).text
            stock_number = stock_text.split("(")[1].split(" ")[0]
            return int(stock_number)
        except Exception as e:
            self.logger.error(f"Error parsing amount in stock from {detail_url}: {e}")
            return 0

    @staticmethod
    def parse_rating(response: Response) -> str:
        return response.css("p.star-rating::attr(class)").get().split(" ")[1]

    def parse_category(self, detail_url: str) -> str:
        self.driver.get(detail_url)
        try:
            breadcrumb_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((
                    By.CSS_SELECTOR, ".breadcrumb li"
                ))
            )
            if len(breadcrumb_elements) > 1:
                category_text = breadcrumb_elements[-2].text
                return category_text
            else:
                return "Unknown Category"
        except Exception as e:
            self.logger.error(f"Error parsing category from {detail_url}: {e}")
            return "Unknown Category"

    def parse_description(self, detail_url: str) -> str:
        self.driver.get(detail_url)
        try:
            description = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, "#product_description ~ p"
                ))
            )
            return description.text.strip()
        except Exception as e:
            self.logger.error(f"Error parsing description from {detail_url}: {e}")
            return "No description available"

    def parse_upc(self, detail_url: str) -> str:
        self.driver.get(detail_url)
        try:
            table_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, ".table.table-striped"
                ))
            )
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                header = row.find_element(By.TAG_NAME, "th").text
                if header == "UPC":
                    upc = row.find_element(By.TAG_NAME, "td").text
                    return upc
            return "UPC not found"
        except Exception as e:
            self.logger.error(f"Error parsing UPC from {detail_url}: {e}")
            return "Error"
