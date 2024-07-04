import scrapy
from scrapy.http import Response
from typing import Generator, Optional


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Generator:
        for product in response.css("article.product_pod"):
            detail_page_url = product.css("h3 a::attr(href)").get()
            if detail_page_url:
                yield response.follow(detail_page_url,
                                      callback=self.parse_detail)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_detail(self, response: Response) -> Generator:
        yield {
            "title": self.get_title(response),
            "price": self.get_price(response),
            "amount_in_stock": self.get_amount_in_stock(response),
            "rating": self.get_rating(response),
            "category": self.get_category(response),
            "description": self.get_description(response),
            "upc": self.get_upc(response),
        }

    @staticmethod
    def get_title(response: Response) -> Optional[str]:
        return response.css("div.product_main h1::text").get()

    @staticmethod
    def get_price(response: Response) -> Optional[str]:
        price = response.css("p.price_color::text").get()
        return price.replace("£", "") if price else None

    @staticmethod
    def get_amount_in_stock(response: Response) -> Optional[str]:
        return response.css("p.availability::text").re_first(r"\d+")

    @staticmethod
    def get_rating(response: Response) -> Optional[str]:
        return response.css("p.star-rating::attr(class)").re_first(
            r"star-rating (\w+)"
        )

    @staticmethod
    def get_category(response: Response) -> Optional[str]:
        return response.css("ul.breadcrumb li:nth-child(3) a::text").get()

    @staticmethod
    def get_description(response: Response) -> Optional[str]:
        return response.css("div#product_description ~ p::text").get()

    @staticmethod
    def get_upc(response: Response) -> Optional[str]:
        return response.css("table.table tr:nth-child(1) td::text").get()
