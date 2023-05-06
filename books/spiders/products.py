import scrapy
from scrapy.http import Response


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            url = book.css("h3 > a::attr(href)").get()
            yield response.follow(url, callback=self.parse_single_book)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_single_book(self, page: Response):
        title = page.css("h1::text").get()
        price = float(
            page.css("p.price_color::text").get().replace("£", "")
        )
        amount_in_stock = int(
            page.css("p.availability::text").re_first(r"([\d]+) available")
        )
        rating = (
            page.css(".product_main > p.star-rating::attr(class)")
            .get().split()[-1]
        )
        category = page.css(".breadcrumb > li > a::text").getall()[-1]
        description = page.css("article.product_page > p::text").get()
        upc = page.css("table tr td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
