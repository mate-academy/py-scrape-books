import scrapy
from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs) -> None:
        image_containers = response.css("div.image_container")

        for container in image_containers:
            relative_link = container.css("a::attr(href)").get()

            if relative_link:
                absolute_link = response.urljoin(relative_link)
                yield scrapy.Request(url=absolute_link, callback=self.parse_page)

        next_page = response.css(".next a::attr(href)").get()

        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    @staticmethod
    def parse_page(response: Response) -> dict:
        product_main = response.css("div.product_main")
        title = product_main.css("h1::text").get()
        price = float(product_main.css("p.price_color::text").get().replace("£", ""))
        amount_in_stock = int(
            response.css(".product_page p::text")
            .getall()[2]
            .split(" ")[14]
            .replace("(", "")
        )
        rating = 0
        if product_main.css("p.One"):
            rating = 1
        elif product_main.css("p.Two"):
            rating = 2
        elif product_main.css("p.Three"):
            rating = 3
        elif product_main.css("p.Four"):
            rating = 4
        elif product_main.css("p.Five"):
            rating = 5

        category = response.css(".breadcrumb a::text").getall()[2]
        description = response.css(".product_page p::text").getall()[10]
        upc = response.css(".table-striped td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
