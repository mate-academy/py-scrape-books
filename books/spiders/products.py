import scrapy
from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    
    @staticmethod
    def parse_rating(rating: str) -> int:
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        return rating_map[rating]

    def parse_detail_page(self, book: Response) -> dict:
        yield {
            "title": book.css("h1::text").get(),
            "price": float(
                book.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                book.css(".instock").get().split()[-3].replace("(", "")
            ),
            "rating": self.parse_rating(
                book.css(".star-rating::attr(class)").get().split()[-1]
            ),
            "category": (
                book.css(".breadcrumb > li:nth-last-child(2) a::text").get()
            ),
            "description": book.css("article > p::text").get(),
            "upc": book.css("td::text").get()
        }

    def parse(self, response: Response, **kwargs):
        for product_url in response.css(
                "ol.row li h3 a::attr(href)"
        ).extract():
            yield scrapy.Request(
                url=response.urljoin(product_url),
                callback=self.parse_detail_page
            )

        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(
                response.urljoin(next_page), callback=self.parse
            )
