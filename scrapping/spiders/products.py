import scrapy
from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]




    def detail_parse(self, response: Response, **kwargs):
        raw_amount = response.css(".instock.availability").re_first(r"\((\d+)\s+available\)")
        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css(".price_color::text").get().strip("£")),
            "amount_in_stock": int(raw_amount) if raw_amount else None,
            "rating": response.css(".star-rating::attr(class)").get().split()[1],
            "category": response.css(".breadcrumb li a::text").getall()[2],
            "description": response.css(".sub-header + p::text").get(),
            "UPC": response.css("tr td::text").get()
        }


    def parse(self, response: Response, **kwargs):
        for url in response.css(".product_pod h3 a::attr(href)").getall():
            yield response.follow(url, callback=self.detail_parse)

        next_page = response.css(".next a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)