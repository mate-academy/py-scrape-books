from dataclasses import dataclass
import asyncio
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


@dataclass
class Book:
    title: str
    price: float
    amount_in_stock: int
    rating: int
    category: str
    description: str
    upc: str


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    async def parse(self, response):
        book_detail_links = response.css(".product_pod > h3 > a")
        for link in book_detail_links:
            yield response.follow(link, self.parse_book)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _get_amount_in_stock(response):
        response = response.css("table.table td::text").getall()[5]
        return int("".join(
            num
            for num in response
            if num.isnumeric()
        ))

    @staticmethod
    def _get_rating(response):
        response = response.css("p.star-rating::attr(class)").get().split()[1]
        numbers = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        return numbers.get(response)

    def parse_book(self, response):
        return Book(
            title=response.css(".product_main > h1::text").get(),
            price=float(response.css("p.price_color::text").get()[1:]),
            amount_in_stock=self._get_amount_in_stock(response),
            rating=self._get_rating(response),
            category=response.css(".breadcrumb > li > a::text").getall()[2],
            description=response.css(".product_page > p::text").get(),
            upc=response.css(".table td::text").getall()[0],
        )


async def run_spider():
    process = CrawlerProcess(get_project_settings())
    await process.crawl(BooksSpider)
    await process.join()


if __name__ == "__main__":
    asyncio.run(run_spider())
