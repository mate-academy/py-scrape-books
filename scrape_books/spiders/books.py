import re

import scrapy

from scrape_books.items import ScrapeBooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    custom_settings = {
        "FEEDS": {
            "books.jl": {"format": "jsonlines", "overwrite": True},
        },
    }

    def parse(self, response, **kwargs):
        for book in response.css(".product_pod"):
            rating_word = book.css(".star-rating::attr(class)").re_first(r'star-rating\s+(\w+)')
            rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
            rating_number = rating_map.get(rating_word, 0)

            title = book.css("h3 a::attr(title)").get()
            price = float(book.css(".price_color::text").get().replace("£", ""))

            book_url = response.urljoin(book.css("h3 a::attr(href)").get())

            yield scrapy.Request(
                book_url,
                callback=self._parse_additional_information,
                meta={
                    "title": title,
                    "price": price,
                    "rating": rating_number,
                },
            )

        next_page = response.css(".pager li.next a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def _parse_additional_information(self, response):
        availability_text = response.xpath(
            "//th[text()='Availability']/following-sibling::td/text()"
        ).get(default="")
        match = re.search(r"\d+", availability_text)
        amount_in_stock = int(match.group()) if match else 0

        category = response.xpath(
            "//ul[@class='breadcrumb']/li[3]/a/text()"
        ).get(default="").strip()

        description = response.css(
            "#product_description + p::text"
        ).get(default="").strip()

        upc = response.css(
            ".table-striped tbody tr:nth-child(1) td:nth-child(2)::text"
        ).get(default="").strip()

        item = ScrapeBooksItem()
        item["title"] = response.meta["title"]
        item["price"] = response.meta["price"]
        item["rating"] = response.meta["rating"]
        item["amount_in_stock"] = amount_in_stock
        item["category"] = category
        item["description"] = description
        item["upc"] = upc

        yield item
