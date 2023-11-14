import re

import scrapy


def parse_detail_page(response):
    amount_string = response.xpath(
        "//div/p[@class='instock availability']/text()"
    ).getall()
    amount = "0"
    for text in amount_string:
        match = re.search(r"(\d+) available", text)
        if match is not None:
            amount = int(match.group(1))

    class_string = response.xpath(
        "//div[@class='col-sm-6 product_main']/p[3]/@class"
    ).get()
    rating = class_string.split()[-1]
    rating_dict = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    rating = rating_dict[rating]

    yield {
        "title": response.xpath("//h1/text()").get(),
        "price": response.xpath(
            "//div/p[@class='price_color']/text()"
        ).get(),
        "amount_in_stock": amount,
        "rating": rating,
        "category": response.xpath(
            "//*[@id='default']/div/div/ul/li[3]/a/text()"
        ).get(),
        "description": response.xpath(
            "//*[@id='content_inner']/article/p/text()"
        ).get(),
        "upc": response.xpath(
            "//th[text()='UPC']/following-sibling::td/text()"
        ).get(),
    }


class QuotesSpider(scrapy.Spider):
    name = "books_catalogue"

    def start_requests(self):
        urls = [
            "https://books.toscrape.com/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        for book in response.xpath("//article[@class='product_pod']"):
            detail_page = book.xpath("./h3/a/@href").get()
            if detail_page is not None:
                detail_page_url = response.urljoin(detail_page)
                yield scrapy.Request(
                    detail_page_url,
                    callback=parse_detail_page,
                )

        next_page = response.xpath(
            "//li[contains(@class, 'next')]/a/@href"
        ).get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
