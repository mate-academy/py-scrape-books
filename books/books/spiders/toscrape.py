from typing import Any, Generator, Dict

import scrapy
from scrapy.http import Response


class ToscrapeSpider(scrapy.Spider):
    name = "toscrape"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(
            self,
            response: Response,
            **kwargs
    ) -> Generator[scrapy.Request, None, None]:
        for book_url in (
                response.css("article.product_pod h3 a::attr(href)")
                .getall()
        ):
            book_page = response.urljoin(book_url)
            yield scrapy.Request(book_page, callback=self.parse_book)

        next_page_url = response.css("li.next a::attr(href)").get()

        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book(self, response: Response) -> Dict["str", Any]:
        yield {
            "title": response.css("h1::text").get(),
            "price":
                response.css(".price_color::text").get().replace("£", ""),
            "amount_in_stock":
                response.css('p.instock.availability::text')
                .getall()[1].split()[2].replace("(",""),
            "rating":
                response.css("p.star-rating::attr(class)").get().split()[-1],
            "category":
                response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description":
                response.css("#product_description + p::text").get(),
            "upc":
                response.css(
                    ".table-striped th:contains('UPC') + td::text"
                ).get(),
        }
