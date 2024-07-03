import scrapy
from scrapy.http import Response

STAR_RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class BooksScraperSpider(scrapy.Spider):
    name = "books_scraper"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for product in response.css("article.product_pod"):
            detail_page_url = product.css("h3 a::attr(href)").get()
            if detail_page_url is not None:
                yield response.follow(
                    detail_page_url, callback=self.parse_single_book
                )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_single_book(self, response: Response):
        yield {
            "title": response.css(".product_main > h1::text").get(),

            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),

            "amount_in_stock": response.css(
                "p.availability::text"
            ).re_first("\d+"),

            "rating": STAR_RATING_MAP[response.css(
                "p.star-rating::attr(class)"
            ).re_first("star-rating (\w+)")],

            "category": response.css(
                ".breadcrumb > li > a::text"
            ).getall()[-1],

            "description": response.css(
                "#product_description + p::text"
            ).get(),

            "upc": response.css("tr:contains('UPC') td::text").get(),
        }
