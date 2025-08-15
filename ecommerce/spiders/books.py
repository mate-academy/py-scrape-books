import scrapy
from scrapy.http import Response

from ..items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, *args, **kwargs) -> dict:
        for book in response.css(".product_pod"):
            item = BookItem()
            item["title"] = book.css("a::attr(title)").get()

            price_class = book.css(".price_color::text").get()
            item["price"] = float(price_class.replace("£", ""))

            rating_class = book.css(".star-rating::attr(class)").get("")
            item["rating"] = rating_class.split()[-1] if rating_class else None

            url_book = response.urljoin(url=book.css("a::attr(href)").get())

            yield scrapy.Request(
                url=url_book,
                callback=self.parse_book,
                meta={"book": item}
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_book(response: Response) -> BookItem:
        item = response.meta["book"]

        num_availability = response.css(
            "p.availability::text"
        ).re_first(r"\d+")
        item["amount_in_stock"] = int(
            num_availability
        ) if num_availability else 0

        breadcrumb_element = response.css("ul.breadcrumb li a::text").getall()
        if len(breadcrumb_element) > 2:
            item["category"] = breadcrumb_element[2]

        item["description"] = response.xpath(
            "//div[@id='product_description']/following-sibling::p/text()"
        ).get()

        item["upc"] = response.css("table.table tr td::text").get()

        yield item
