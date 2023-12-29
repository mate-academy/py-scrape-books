import scrapy
from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for product in response.css(".product_pod"):
            detail_page = product.css("h3 a::attr(href)").get()
            yield response.follow(detail_page, self.parse_detail_product)

        next_page = response.css(".pager > li")[-1].css("a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_detail_product(product: Response) -> dict:
        breadcrumbs = product.css("ul.breadcrumb li a::text").getall()
        category = " > ".join(breadcrumbs[2:])

        yield {
            "title": product.css("h1::text").get(),
            "price": product.css(".price_color::text").get().replace("£", ""),
            "amount_in_stock":
                product.css("p.availability").get().split()[-3].replace("(", ""),
            "rating": len(product.css(".star-rating::text").getall()),
            "category": category,
            "description":
                product.css("#product_description + p::text").get().strip(),
            "upc": len(product.css("td::text").get()),
        }
