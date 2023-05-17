
from typing import Generator
import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs) -> Generator:

        for book_url in response.css(".product_pod > h3 > a::attr(href)").extract():
            book_url = response.urljoin(book_url)

            yield scrapy.Request(url=book_url, callback=self.parse_single_product)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)

            yield scrapy.Request(next_page, callback=self.parse)

    @staticmethod
    def parse_single_product(response: Response) -> Generator:
        rating_num = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(response.css(".product_main > .price_color::text").get().strip("£")),
            "in_stock": int(response.css(
                ".product_main > p.instock.availability::text"
            ).getall()[1].strip().split()[-2].strip('(')),
            "rating": rating_num.get(response.css(".product_main > .star-rating").get().split()[2].strip('">'), 0),
            "category": response.css(".breadcrumb > li > a::text").getall()[2],
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(
                ".table-striped ").get().split()[4].strip("<th>UPC</th><td>").strip("</td>"),
        }
