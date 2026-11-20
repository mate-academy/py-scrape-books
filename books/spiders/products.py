import re

import scrapy


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        for book in response.css("article.product_pod"):
            yield response.follow(
                book.css("h3 a::attr(href)").get(),
                callback=self.parse_book
            )

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse
            )

    def parse_book(self, response):
        # rating_class = response.css(
        #     "p.star-rating::attr(class)"
        # ).get()
        #
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        #
        # rating = rating_class.split()[-1] if rating_class else None

        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),

            # "amount_in_stock": int(
            #     response.css(".availability::text").get().rstrip("In stock (").lstrip(" available)")
            # ),
            # "rating": rating_map.get(rating),
            # "category": response.css("ul.breadcrumb li:nth-last-child(2) a::text").get(),
            # "description": response.css(".product_page p::text").get(),
            # "upc": response.xpath("//th[text()='UPC']/following-sibling::td/text()").get()
            "amount_in_stock": int(
                re.search(
                    r"\((\d+)",
                    " ".join(response.css(".availability::text").getall())
                ).group(1)
            ),

            "rating": rating_map.get(
                response.css(".star-rating::attr(class)").get().split()[-1]
            ),

            "category": response.css(
                "ul.breadcrumb li:nth-last-child(2) a::text"
            ).get(),

            "description": response.xpath(
                '//div[@id="product_description"]/following-sibling::p[1]/text()'
            ).get(),

            "upc": response.xpath(
                "//th[text()='UPC']/following-sibling::td/text()"
            ).get()
        }
