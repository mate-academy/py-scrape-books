from bs4 import BeautifulSoup
import requests
import scrapy
from scrapy import Selector
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for product in response.css(".product_pod"):
            yield self._result(response=response, product=product)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def _result(self, response: Response, product: Selector):
        book_info = self._parce_detail_page(response, product)
        book_info["title"] = product.css("a::attr(title)").get()
        book_info["price"] = float(product.css(".price_color::text").get().lstrip("£"))

        return book_info

    def _parce_detail_page(self, response: Response, product: Selector) -> dict:
        detailed_url = response.urljoin(product.css("a::attr(href)").get())
        page = requests.get(detailed_url).content
        soup = BeautifulSoup(page, "html.parser")
        book_info = dict()
        book_info["upc"] = soup.select_one("tr:first-child > td").text
        book_info["category"] = soup.select(".breadcrumb > li")[-2].select_one("a").text
        book_info["rating"] = self._parce_rating(soup)
        book_info["amount_in_stock"] = soup.select_one(".instock").text.split()[-2].lstrip("(")
        description_tag = soup.select_one("#product_description + p")
        book_info["description"] = description_tag.text if description_tag else None

        return book_info

    @staticmethod
    def _parce_rating(soup: BeautifulSoup) -> int:
        help_dict = {
            "zero": 0,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
        }
        word_number = soup.select_one("p.star-rating")["class"][-1].lower()

        return help_dict[word_number]
