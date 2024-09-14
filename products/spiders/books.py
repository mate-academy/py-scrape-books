from typing import Dict, Any, Iterator

import scrapy
from scrapy.http import Response


RATING = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Iterator[Any]:
        for book in response.css(".product_pod"):
            book_detail_url = response.urljoin(book.css("h3 a::attr(href)").get())
            yield response.follow(book_detail_url, callback=self._parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _parse_book(response: Response) -> Iterator[Dict[str, Any]]:
        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css("p.price_color::text").get().replace("£", "")),
            "amount_in_stock": int(response.css("p.availability::text").re_first("\d+")),
            "rating": RATING.get(response.css("p.star-rating::attr(class)").get().split()[-1]),
            "category": response.css("ul.breadcrumb li a::text").getall()[-1],
            "description":response.css("div#product_description ~ p::text").get(),
            "upc": response.css("table.table tr:nth-child(1) td::text").get(),
        }
