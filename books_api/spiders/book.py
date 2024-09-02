import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"
                  "catalogue/category/books_1/index.html"]

    def parse(self, response: Response, **kwargs) -> None:

        book_links = response.css(".product_pod a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book_details)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    @staticmethod
    def parse_book_details(response: Response) -> dict:
        book_export = {
            "title": response.css("h1::text").get(),
            "price": response.css(".price_color::text").get()[1::],
            "amount_in_stock":
                response.css("p.availability::text").re_first(r"\d+"),
            "rating":
                response.css(".star-rating::attr(class)").get().split(" ")[-1],
            "category":
                response.css(".breadcrumb > li > a::text").getall()[-1],
            "description": response.css("article > p::text").get(),
            "UPC": response.css("tr > td::text").getall()[0],
        }
        return book_export
