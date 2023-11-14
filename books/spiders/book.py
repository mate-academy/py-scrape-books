import scrapy

from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> scrapy.Request:
        book_links = response.css(".product_pod h3 a::attr(href)").extract()
        for book_link in book_links:
            yield scrapy.Request(
                response.urljoin(book_link), callback=self.parse_book
            )

        for link in response.css("li.next a::attr(href)"):
            yield response.follow(link, self.parse)

    @staticmethod
    def extract_numeric_rating(response: scrapy.http.Response) -> int:
        rating_class = response.css(".star-rating::attr(class)").get().split()
        ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        return ratings[rating_class[1]]

    @staticmethod
    def extract_amount_in_stock(response: Response) -> int | str:
        availability_text = response.css(
            ".table-striped tr:nth-child(6) td::text"
        ).get()
        if "In stock" in availability_text:
            amount_in_stock = availability_text.split("(")[-1].split()[0]
            return amount_in_stock
        else:
            return "Not available"

    def parse_book(self, response: Response) -> dict:
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css(".price_color::text").get().replace("£", ""),
            "amount_in_stock": self.extract_amount_in_stock(response),
            "rating": self.extract_numeric_rating(response),
            "category": response.css(
                ".breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(
                ".table-striped tr:nth-child(1) td::text"
            ).get(),
        }
