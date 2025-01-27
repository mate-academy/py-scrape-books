import scrapy
from scrapy.http import Response
import re

from books.items import Book

RATING_NUMS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class ScrapeBooksSpider(scrapy.Spider):
    name = "scrape_books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs):
        detail_urls = response.css(".product_pod a::attr(href)").getall()
        yield from response.follow_all(detail_urls, callback=self.parse_details)

        pagination_links = response.css("li.next a::attr(href)").getall()
        yield from response.follow_all(pagination_links, callback=self.parse)

    def parse_details(self, response: Response, **kwargs):
        category_scraped = response.xpath("//*[@id='default']/div/div/ul/li[3]//text()").getall()
        category = "".join(elem.strip() for elem in category_scraped)

        stock_info = response.xpath("//*[@id='content_inner']/article/div[1]/div[2]/p[2]/text()").getall()
        amount_str = [text.strip() for text in stock_info if text.strip()]
        amount_in_stock = int(re.findall(r"\d+", "".join(amount_str))[0])

        description = response.xpath("//*[@id='content_inner']/article/p/text()").get()

        upc = response.xpath("//*[@id='content_inner']/article/table/tr[1]/td/text()").get()

        for content in response.css(".content"):
            title = content.css(".col-sm-6.product_main h1::text").get()
            price = float(content.css(".price_color::text").get().replace("£", ""))

            rating_class = content.css(".star-rating::attr(class)").get()
            rating = RATING_NUMS[rating_class.split(" ")[-1]]

            book = Book(
                title=title,
                price=price,
                amount_in_stock=amount_in_stock,
                rating=rating,
                category=category,
                description=description,
                upc=upc
            )

            yield book
