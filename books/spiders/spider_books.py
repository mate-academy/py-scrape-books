import scrapy
from scrapy.http import Response

RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class SpiderBooksSpider(scrapy.Spider):
    name = "spider-books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for href in response.css("article.product_pod h3 a::attr(href)").getall():
            yield response.follow(href, self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    @staticmethod
    def parse_book(response: Response):
        title = response.css("div.product_main h1::text").get()
        price = (
            response.css("div.product_main p.price_color::text").get().replace("£", "")
        )
        stock = response.css("div.product_main p.availability::text").re_first(
            r"(\d+) available"
        )
        rating_in_words = response.css(
            "div.product_main p.star-rating::attr(class)"
        ).re_first(r"star-rating ([A-Za-z]+)")
        rating = RATING[rating_in_words]
        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        description = response.css("div#product_description + p::text").get()
        upc = response.css("table tr:nth-child(1) td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
