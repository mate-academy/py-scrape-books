from time import sleep
from books.items import BookItem

import scrapy
from scrapy.http import Response


XPATH_URL_BOOK_LINK = "//section/div/ol/li/article/h3/a/@href"
XPATH_URL_NEXT_PAGE = "//div/ul/li/a/@href"
XPATH_URL_SIDE_BAR = "//aside/div/ul/li/ul/li/a/@href"

BASE_URL = "https://books.toscrape.com/"
BASE_URL_CATALOGUE = "https://books.toscrape.com/catalogue/"

THROTTLING_TIME = 0.1

RATING_DICT = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> dict:

        for link in response.xpath(XPATH_URL_BOOK_LINK).getall():

            if "catalogue/" in link:
                full_link = BASE_URL + link
            else:
                full_link = BASE_URL_CATALOGUE + link

            yield response.follow(
                full_link, callback=self.get_all_info_from_book_page
            )

        next_page = response.xpath(XPATH_URL_NEXT_PAGE).getall()[-1]

        if next_page is not None:
            sleep(THROTTLING_TIME)

            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def get_all_info_from_book_page(self, response: Response) -> dict:

        yield BookItem(
            title=response.css(".product_main h1::text").get(),
            price=response.css("p.price_color ::text").get(),
            amount_in_stock=response.xpath("//tr/td/text()").getall()[5],
            rating=RATING_DICT.get(
                response.css("p.star-rating::attr(class)").get().split()[-1]
            ),
            category=response.css("ul.breadcrumb > li > a::text").getall()[2],
            description=response.xpath("//article/p/text()").get(),
            upc=response.xpath("//tr/td/text()").getall()[5]
        ).__dict__
