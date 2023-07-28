import scrapy
from scrapy.http import Response

RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class AllBookSpider(scrapy.Spider):
    name = "all_book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        for href in response.css(
                "article.product_pod h3 a::attr(href)"
        ).getall():
            yield response.follow(href, self.get_book)

        next_page_url = response.css(".next a::attr(href)").get()
        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse)

    @staticmethod
    def get_book(response: Response) -> None:
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": response.css(".price_color::text").get().replace("£", ""),
            "amount_in_stock": response.css(
                ".product_main .availability::text"
            ).re_first(r"(\d+) available"
                       ),
            "rating": RATING[response.css(
                ".star-rating::attr(class)"
            ).get().split(" ")[-1]],
            "category": response.css(
                ".breadcrumb > li:nth-child(3)::text"
            ).get(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(
                "tbody > tr > thp:nth-child(1) > td::text"
            ).get(),
        }
