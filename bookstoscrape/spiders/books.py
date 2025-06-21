import logging
import sys

from enum import Enum
from urllib.parse import urljoin
import scrapy
from scrapy.http import Response
from scrapy.selector import Selector
from selenium import webdriver


logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout),
    ]
)


class RatingEnum(Enum):
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = webdriver.Firefox()

    def close(self, reason: str):
        if hasattr(self, "driver"):
            try:
                self.driver.quit()
            except Exception:
                pass

    def parse(self, response: Response, **kwargs):
        switch_page = urljoin(self.start_urls[0], "catalogue/")

        for book in response.css(".product_pod"):
            book_link = book.css("a[title]").attrib["href"]

            logging.info(f"Book link: {book_link}")

            if book_link.split("/")[0] != "catalogue":
                book_link = f"catalogue/{book_link}"
                logging.info(f"book_link was changed: {book_link}")
            # find on book page:  amount_in_stock, category,  description, upc
            amount_in_stock, category, description, upc = (
                self._parse_one_book_page(book_link)
            )

            yield {
                "title": book.css("a[title]").attrib["title"],
                "price": float(
                    book.css("p.price_color::text").get().replace("£", "")
                ),
                "amount_in_stock": amount_in_stock,
                "rating": RatingEnum[book.css(
                    ".star-rating::attr(class)"
                ).get().split()[1]].value,
                "category": category,
                "upc": upc,
                "description": description
            }
        try:
            next_page = urljoin(
                switch_page, response.css(
                    "li.next a::attr(href)"
                ).get().split("/")[-1]
            )
            logging.info(f"Scrapping  PAGE: {next_page}")

            yield response.follow(next_page, callback=self.parse)
        except AttributeError:
            logging.info("Scrapping finished...")

    def _parse_one_book_page(
            self, book_link: str
    ) -> tuple[int, str, str, str]:

        url = urljoin(self.start_urls[0], book_link)

        logging.info(f"Scrapping  BOOK page: {url}")

        self.driver.get(url)
        selector = Selector(
            text=self.driver.page_source.encode(
                "utf-8", errors="ignore").decode("utf-8")
        )

        description = selector.css(
            "article.product_page p:not([class])::text"
        ).get()
        amount_in_stock = int(
            selector.css(
                "p.instock.availability::text"
            ).getall()[1].split("(")[1].split()[0]
        )
        category = selector.css(
            "ul.breadcrumb li"
        ).getall()[-2].split(">")[-3].split("<")[0]
        upc = selector.css("table.table-striped td::text").get()

        return (amount_in_stock, category, description, upc)
