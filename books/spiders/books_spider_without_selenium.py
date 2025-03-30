import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books_2"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> dict:
        for product in response.css(".row > li"):
            url_product = product.css("h3 > a::attr(href)").get()
            yield response.follow(url_product, callback=self.parse_book)


        next_url_page = response.css(".next > a::attr(href)").get()
        if next_url_page is not None:
            yield response.follow(next_url_page, callback=self.parse)

    @staticmethod
    def parse_book(response: Response):
        rating_dict = {
            "Zero": 0, "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
        }
        title = response.css(".product_main > h1::text").get()
        price = float(response.css(".price_color::text").get().replace("£", ""))
        amount_in_stock = int(response.css(".instock::text")
                              .getall()[1]
                              .strip()
                              .split()[2]
                              .replace("(", "")
                              )
        rating = response.css(".star-rating::attr(class)").get().split()[1]
        category = response.css(".breadcrumb > li > a::text").getall()[-1]
        description = response.css("#product_description + p::text").get()
        upc = response.css(".table-striped tr:nth-child(1) td::text").get()
        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating_dict[rating],
            "category": category,
            "description": description,
            "upc": upc
        }
