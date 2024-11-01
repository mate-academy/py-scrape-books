import re

import scrapy

RATING_MAPPER = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response, **kwargs):
        total_pages = response.css(
            "li.current::text"
        ).re_first(r"Page \d+ of (\d+)")
        if total_pages:
            total_pages = int(total_pages)
        else:
            total_pages = 1
        for page in range(1, total_pages + 1):
            url = f"https://books.toscrape.com/catalogue/page-{page}.html"
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        for book_url in response.css(
                ".image_container > a::attr(" "href)"
        ).getall():
            url = "https://books.toscrape.com/catalogue/" + book_url
            yield scrapy.Request(url=url, callback=self.parse_book_page)

    def parse_book_page(self, response):
        title = response.css(".active::text").get().strip()
        price = float(response.css(
            ".price_color::text"
        ).get().replace("£", ""))
        amount_in_stock = int(
            re.search(
                r"\d+", "".join(response.css(
                    ".availability *::text"
                ).getall()).strip()
            ).group()
        )
        rating = RATING_MAPPER.get(
            response.css("p.star-rating::attr(" "class)").get().split()[-1]
        )
        category = response.css("ul.breadcrumb li a::text").getall()[-1]
        description = response.css(
            'meta[name="description"]::attr(content)'
        ).get()
        upc = response.css(
            'table.table-striped tr:contains("UPC") td::text'
        ).get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
