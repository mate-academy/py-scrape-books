import scrapy
from scrapy.http.response import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self) -> None:
        super().__init__()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def close(self, reason: str) -> None:
        self.driver.close()

    def parse(self, response: Response, **kwargs: dict) -> None:
        for book in response.css(".product_pod"):
            detailed_url = response.urljoin(
                book.css(".product_pod h3 a::attr(href)").get()
            )
            self.driver.get(detailed_url)

            description_element = self.driver.find_elements(
                By.CSS_SELECTOR, "div > article > p"
            )
            description = (
                description_element[0].text if description_element else None
            )

            yield {
                "title": book.css("a::attr(title)").get(),
                "price": float(
                    book.css(".price_color::text").get().replace("£", "")
                ),
                "amount_in_stock": self._parse_single_book(response, book)[
                    "amount_in_stock"
                ],
                "rating": book.css("p::attr(class)")
                .get()
                .replace("star-rating ", ""),
                "category": response.css(".nav-list > li a::text")
                .get()
                .strip(),
                "description": description,
                "upc": self._parse_single_book(response, book)["upc"],
            }

        next_page = response.css("li.next a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_single_book(self) -> dict[str, str]:
        detail_info = dict()
        detail_info["amount_in_stock"] = int(
            self.driver.find_element(By.CLASS_NAME, "availability").text.split(
                "("
            )[-1][:-11]
        )
        detail_info["upc"] = self.driver.find_element(
            By.CSS_SELECTOR, ".table td"
        ).text

        return detail_info
