import scrapy

class BookScrapy(scrapy.Spider):
    name = "books"
    start_urls = [
        "https://books.toscrape.com",
        "https://books.toscrape.com/catalogue/page-2.html"
    ]

    def parse(self, response):
        for book in response.css("article.product_pod"):
            yield {
                "title": book.css("h3 a::attr(title)").get(),
                "price": book.css("p.price_color::text").get(),
                "amount_in_stock": book.css("p.instock.availability::text").get().strip(),
                "rating": book.css("p.star-rating::attr(class)").get().split()[-1],
                "category": book.css(".breadcrumb::text").get(),
                "description": book.css("#product_description + p::text").get(),
                "upc": book.css("table.table.table-striped tr:nth-child(1) td::text").get(),
            }