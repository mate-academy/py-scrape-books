import scrapy
import re
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    _rating_mapper = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(self, response: Response, **kwargs) -> dict[str]:
        for book in response.css("li.col-xs-6"):
            detailed_url = response.urljoin(
                book.css("h3 > a::attr(href)").get()
            )
            rating = (
                book.css(".image_container + p")
                .xpath("@class")
                .extract()[0]
                .split()[-1]
            )
            book_data = {
                "title": book.css("h3 > a::attr(title)").get(),
                "price": float(
                    book.css(".product_price > .price_color::text").get()[1::]
                ),
                "rating": self._rating_mapper[rating],
            }
            yield scrapy.Request(
                detailed_url,
                callback=self._parse_detail,
                meta={"book_data": book_data}
            )

        next_page = response.css(".pager > .next").css("a::attr(href)").get()

        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def _parse_detail(self, response: Response, **kwargs) -> dict[str]:
        table_data = response.xpath("//table/tr/td//text()").getall()

        yield {
            **response.meta["book_data"],
            "amount_in_stock": int(
                re.search(r"(\d+)", table_data[5]).group(1)
            ),
            "category": response.xpath(
                "//ul[@class='breadcrumb']/li/a//text()"
            ).getall()[2],
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": table_data[0],
        }
