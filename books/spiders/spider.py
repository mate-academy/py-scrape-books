import requests
import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Response


class SpiderSpider(scrapy.Spider):
    name = "spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def _parse_single_book(self, url: str) -> dict:
        page = requests.get(url).content
        page_soup = BeautifulSoup(page, "html.parser")

        table_values = page_soup.select("table.table > tr > td")

        return {
            "category": page_soup.select("ul.breadcrumb > li")[2]
            .text.replace("\n", ""),
            "description": page_soup.find(
                "meta", {"name": "description"}
            )["content"].replace("\n", ""),
            "upc": table_values[0].text,
            "amount_in_stock": int(
                table_values[5].text
                .split("(")[1]
                .split()[0]
            ),
        }

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            numbers = {
                "One": 1,
                "Two": 2,
                "Three": 3,
                "Four": 4,
                "Five": 5
            }
            rating = book.css("p.star-rating::attr(class)").get().split()[-1]
            general = {
                "title": book.css("a::attr(title)").get(),
                "price": float(
                    book.css(".price_color::text").get().replace("£", "")
                ),
                "rating": numbers.get(rating, 0),
            }
            detail = self._parse_single_book(
                response.urljoin(
                    book.css("a::attr(href)").get()
                )
            )
            general.update(detail)

            yield general

        next_page = response.css("li.next > a::attr(href)").get()

        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)
