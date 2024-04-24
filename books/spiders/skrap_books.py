from typing import Generator

import scrapy
from scrapy.http import Response


ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class SkrapBooksSpider(scrapy.Spider):
    name = "skrap_books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Generator:
        product_pod = response.css(".product_pod")

        for book in product_pod:
            book_detail_url = book.css("h3 a::attr(href)").get()
            yield scrapy.Request(
                url=response.urljoin(book_detail_url), callback=self._parse_single_book
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def _parse_single_book(self, response: Response) -> Generator:
        title = response.css(".product_main > h1::text").get()
        price = response.css(".price_color::text").get()
        amount_in_stock = response.xpath("//tr/td/text()").getall()[5]
        rating = ratings.get(
            response.css(".star-rating::attr(class)").get().split()[1], 0
        )
        category = response.css(".breadcrumb > li > a::text").getall()[2]
        description = response.xpath('//*[@id="content_inner"]/article/p/text()').get()
        upc = response.css(".table.table-striped > tr")[0].css("td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
