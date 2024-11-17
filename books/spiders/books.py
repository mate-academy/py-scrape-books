import scrapy
from scrapy import Request
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = [
        "https://books.toscrape.com",
    ]

    def parse(self, response: Response, **kwargs):
        for book in response.css("ol.row > li.col-xs-6"):
            book_url = response.urljoin(book.css("h3 > a::attr(href)").get())
            help_dict_rating = {
                "One": 1,
                "Two": 2,
                "Three": 3,
                "Four": 4,
                "Five": 5,
            }
            book_data = {
                "title": book.css("a::attr(title)").get(),
                "price": float(book.css("p.price_color::text").get().replace("£", "")),
                "rating": help_dict_rating[
                    book.css("p.star-rating::attr(class)").get().split()[-1]
                ],
            }

            yield Request(
                url=book_url,
                callback=self.get_individual_book_info,
                meta={"book_data": book_data},
            )

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def get_individual_book_info(self, response: Response):
        book_data = response.meta["book_data"]
        amount_in_stock = response.css("td::text").getall()[-2]
        category = response.css("td::text").getall()[1]
        description = response.css("article.product_page > p::text").get()
        upc = response.css("td::text").getall()[0]
        book_data["amount_in_stock"] = amount_in_stock
        book_data["upc"] = upc
        book_data["description"] = description
        book_data["category"] = category
        yield book_data
