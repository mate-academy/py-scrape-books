import scrapy
from scrapy.http import Response

RATING_NUMBER = {
    "Zero": 0,
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksspiderSpider(scrapy.Spider):
    name = "booksspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod h3 a::attr(href)").getall():
            yield scrapy.Request(
                response.urljoin(book),
                callback=self.parse_details
            )
            next_page = response.css("lu.next a::attr(href)").get()
            if next_page is not None:
                yield response.follow(next_page, self.parse)

    @staticmethod
    def parse_details(response: Response) -> dict:
        title = response.css(".product_main h1::text").get()
        price = float(response.css(".price_color::text").get().replace("£", ""))
        amount_in_stock = response.css(".availability::text").re_first(r'\d+')
        rating = RATING_NUMBER.get(response.css("p.star-rating::attr(class)").get().split()[-1])
        category = response.css(".breadcrumb li a::text").getall()[-1]
        description = response.css("#product_description + p::text").get()
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
