import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            yield scrapy.Request(
                response.urljoin(book.css("a::attr(href)").get()),
                callback=self.parse_detail,
            )

        if next_page := response.css(".next a::attr(href)").get():
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_detail(response: Response) -> dict:
        return {
            "title": response.css(".product_main h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(response.css(
                ".availability::text").re_first(r"\d+")
            ),
            "rating": response.css(".star-rating::attr(class)")
            .get()
            .split(" ")[1],
            "category": response.css(
                ".breadcrumb > li:nth-child(3) a::text"
            ).get(),
            "description": response.css("article > p::text").get(),
            "upc": response.css("td::text").get(),
        }
