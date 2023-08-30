import scrapy
from scrapy.http import Response

from books.items import BooksItem


class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        book_links = response.css("h3 > a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, self.parse_book)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> None:
        item = BooksItem()
        item["title"] = response.css("h1::text").get()
        item["price"] = response.css(".price_color::text").get()
        item["amount_in_stock"] = (
            response.css(
                "p.instock.availability"
            ).xpath("normalize-space()").get()
        )
        item["rating"] = (
            response.css("p.star-rating::attr(class)")
            .get()
            .replace("star-rating", "")
            .strip()
        )
        item["category"] = response.css(
            "ul.breadcrumb > li:nth-child(3) > a::text"
        ).get()
        item["description"] = (
            response.css(
                'meta[name="description"]::attr(content)'
            ).get().strip()
        )
        item["upc"] = response.css("td::text")[0].get()
        yield item
