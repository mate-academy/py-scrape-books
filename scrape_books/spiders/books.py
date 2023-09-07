from urllib.parse import urljoin

import scrapy
from scrapy import Selector
from scrapy.http import Response
import requests
from bs4 import BeautifulSoup


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: Response, **kwargs) -> dict:
        for book in response.css(".product_pod"):
            yield self._get_detail_info(response=response, book=book)

        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _get_detail_info(
            response: Response,
            book: Selector
    ) -> dict:
        ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        detail_url = book.css("h3 > a::attr(href)").get()
        full_detail_url = urljoin(response.url, detail_url)

        page = requests.get(full_detail_url).content
        soup = BeautifulSoup(page, "html.parser")

        return {
            "title": soup.select_one("h1").text,
            "price": float(
                soup.select_one(".price_color").text[1:]
            ),
            "amount_in_stock": int(
                soup.find_all("td")[-2].text.split()[-2][1:]
            ),
            "rating": ratings.get(
                soup.select_one(".star-rating")["class"][-1]
            ),
            "category": soup.select(".breadcrumb > li > a")[-1].text,
            "description": soup.select_one(".product_page > p").text
            if soup.select_one(".product_page > p")
            else "No descriptions",
            "upc": soup.find_all("td")[0].text,
        }
