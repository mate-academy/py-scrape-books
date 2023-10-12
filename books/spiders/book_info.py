import scrapy

from scrapy.http import Response


class BookInfoSpider(scrapy.Spider):
    name = "book_info"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/category/books_1/"]

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod "):
            href = book.css("a ::attr(href)").get()
            yield response.follow(href, callback=self.parse_books)

        next_page = response.css(".next").css("a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_books(self, response: Response) -> None:
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": float(
                response.css(".product_main")
                .css(".price_color::text").get()[1:]
            ),
            "amount_in_stock": int(
                response.css(".table-striped tr")[5]
                .css("td::text")
                .get()
                .split()[2][1:]
            ),
            "rating": self._check_rating(response=response),
            "category": response.css(".breadcrumb li")[2].css("a::text").get(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table-striped tr")[0].css("td::text").get(),
        }

    def _check_rating(self, response: Response) -> int:
        rating = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        pars_rating = (
            response.css(".product_main .star-rating::attr(class)")
            .get().split()[-1]
        )
        return ([value for key, value in rating.items()
                 if key == pars_rating][0])
