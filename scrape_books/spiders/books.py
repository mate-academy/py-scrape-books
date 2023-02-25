from collections.abc import Generator

import requests
import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    rating = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def parse(self, response: Response, **kwargs) -> Generator[dict, None, None]:
        for book_url in response.css(".product_pod h3 a::attr(href)").getall():
            page_soup = self._parse_book_page_detail(book_url, response)
            yield {
                "title": page_soup.select_one(".product_main > h1").text,
                "price": float(
                    page_soup.select_one(".price_color").text.replace("£", "")
                ),
                "amount_in_stock": int(
                    page_soup.select_one(
                        ".instock"
                    ).text.split()[2].replace("(", "")
                ),
                "rating": self.rating[page_soup.select_one(
                    ".star-rating"
                ).attrs["class"][1]],
                "category": page_soup.select(
                    ".breadcrumb > li"
                )[2].text.replace("\n", ""),
                "description": page_soup.select_one(".product_page > p").text
                if page_soup.select_one("#product_description") else None,
                "upc": page_soup.select(
                    ".table > tr > td"
                )[0].text.replace("\n", ""),
            }

        next_page = response.css(".pager > li.next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _parse_book_page_detail(
            book_url: str, response: Response
    ) -> BeautifulSoup:
        detailed_url = response.urljoin(book_url)
        page = requests.get(detailed_url).content
        return BeautifulSoup(page, "lxml")
