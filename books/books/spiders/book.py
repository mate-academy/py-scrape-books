import requests
from bs4 import BeautifulSoup
import scrapy
from scrapy.http import Response

numbers_to_int = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_information = book.css("a::attr(href)").get()
            yield self._get_all_info(response, book_information)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def _get_all_info(self, response: Response, detail_url: str) -> dict:
        detail_url = response.urljoin(detail_url)
        detailed_page = requests.get(detail_url)
        soup = BeautifulSoup(detailed_page.content, "html.parser")
        return {
            "title": soup.select_one(".col-sm-6.product_main > h1").text,
            "price": float(soup.select_one(".col-sm-6.product_main > .price_color").text.replace("£", "")),
            "amount_in_stock": int(
                soup.select_one(".col-sm-6.product_main > .instock.availability").text.strip().split()[-2][1:]
            ),
            "rating": int(
                numbers_to_int[soup.select_one(".col-sm-6.product_main > .star-rating").get("class")[1].lower()]
            ),
            "description": soup.select_one("#product_description + p").text if soup.select_one("#product_description + p") else None,
            "upc": soup.select_one(".table.table-striped").select_one("tr > td").text
        }

# price
# amount_in_stock
# rating
# category
# description
# upc
