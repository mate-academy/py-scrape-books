import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        for book_detail_link in response.css("h3 > a::attr(href)").getall():
            yield response.follow(
                book_detail_link, callback=self.parse_book_info
            )

    @staticmethod
    def parse_book_info(response: Response) -> None:
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css(".price_color::text").get(),
            "amount_in_stock": response.css(".instock::text").re_first(r"\d+"),
            "rating": response.css(".star-rating::attr(class)").get()
            .split(" ")[-1],
            "category": response.css(".breadcrumb > li")[2].css("a::text")
            .get(),
            "description": response.css("#product_description ~ p::text")
            .get(),
            "upc": response.css(".table-striped > tr")[0].css("td::text")
            .get(),
        }
