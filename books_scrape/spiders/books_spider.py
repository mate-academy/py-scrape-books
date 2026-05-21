from typing import AsyncIterator, Any

import scrapy
from scrapy.http import Response

rating_dict = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5
}


class BookItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    amount_in_stock = scrapy.Field()
    category = scrapy.Field()
    upc = scrapy.Field()
    description = scrapy.Field()


class BooksSpider(scrapy.Spider):
    name = "books"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.catalogue_url = "https://books.toscrape.com/catalogue/"

    async def start(self) -> AsyncIterator[Any]:
        for page_num in range(1, 51):
            full_url = f"{self.catalogue_url}page-{page_num}.html"
            yield scrapy.Request(url=full_url, callback=self.parse)

    def parse_book_detail(
            self, response: Response
    ) -> Any:
        book_item = BookItem()
        book_item["title"] = response.css(".product_main h1::text").get()
        price_unformatted = response.css(".price_color::text").get()
        book_item["price"] = price_unformatted.replace("£", "")
        rating_unformatted = (
            response.css(".star-rating::attr(class)").get()
        )
        book_item["rating"] = rating_dict.get(
            rating_unformatted.split(" ")[-1].lower()
        )
        amount_in_stock_unformatted = (
            response.css(".instock::text").getall()[1].strip()
        )
        book_item["amount_in_stock"] = (
            amount_in_stock_unformatted.replace("(", "").split()
        )[2]
        book_item["category"] = (
            response.css(".breadcrumb > li > a::text").getall()
        )[-1]
        book_item["upc"] = response.css("td::text").get()
        book_item["description"] = (
            response.css(".product_page > p::text").get()
        )
        yield book_item

    def parse(self, response: Response, **kwargs: Any) -> Any:
        products_pod_css = response.css(".product_pod")
        for product in products_pod_css:
            detail_url = (f"{self.catalogue_url}"
                          f"{product.css("a::attr(href)").get()}")
            yield scrapy.Request(
                url=detail_url, callback=self.parse_book_detail
            )
