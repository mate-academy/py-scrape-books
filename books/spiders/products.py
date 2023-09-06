import scrapy
from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> str:
        for product in response.css(".product_pod"):
            detail_page = response.urljoin(
                product.css("h3 > a::attr(href)").get()
            )
            yield response.follow(
                detail_page, callback=self.parse_detail_product
            )
        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_detail_product(self, response: Response) -> dict:
        rating = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        yield {
            "title": response.css(".h1::text").get(),
            "price": float(response.css(".price_color::text").get()[1:]),
            "amount_in_stock": int(
                response.css(".instock").get().split()[-3][1:]
            ),
            "rating": rating[
                (response.css(".star-rating::attr(class)").get()).split()[-1]
            ],
            "category": response.css(
                ".breadcrumb li:nth-child(3) a::text"
            ).get(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table td::text").get(),
        }
