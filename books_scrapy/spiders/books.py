import os
import subprocess
from typing import Generator

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "library"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    def parse(
            self,
            response: Response, **kwargs
    ) -> Generator[scrapy.Request, None, None]:
        for book in response.css(".product_pod"):
            url = book.css("h3 > a::attr(href)").get()

            if url is not None:
                book_url = response.urljoin(url)
                yield scrapy.Request(book_url, callback=self.get_detail_info)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    @staticmethod
    def get_detail_info(response: Response) -> Generator[dict, None, None]:
        book_exp = {
            "title": response.css(".product_main > h1::text").get(),
            "price": response.css(".price_color::text").get()[1:],
            "amount_in_stock": response.css(
                "p.availability::text"
            ).re_first(r"\d+"),
            "rating": response.css(
                ".star-rating::attr(class)"
            ).get().split(" ")[-1],
            "category": response.css(
                ".breadcrumb > li > a::text"
            ).getall()[-1],
            "description": response.css("article > p::text").get(),
            "upc": response.css(".table tr")[0].css("td::text").get()
        }
        yield book_exp

    def close(self, reason: str) -> None:
        if os.path.exists("books.jl"):
            subprocess.run(["git", "add", "books.jl"])
            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    "Update books.jl with latest scraping results"
                ]
            )
