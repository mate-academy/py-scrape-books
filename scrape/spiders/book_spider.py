import scrapy
from scrapy.http.response import Response
from selenium import webdriver


class BookSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    RATING = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def __init__(self, *args, **kwargs) -> None:
        super(BookSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Edge()

    def closed(self, *args, **kwargs) -> None:
        self.driver.close()

    def parse(self, response: Response) -> None:
        books = response.css("article.product_pod")

        for book in books:
            book_url = book.css("h3 a::attr(href)").get()
            book_url = response.urljoin(book_url)
            yield scrapy.Request(book_url, callback=self.get_all_values)

        next_page = response.css("li.next a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def get_all_values(self, response: Response) -> dict:
        yield {
            "title": self.parse_titles(response=response),
            "price": self.parse_prices(response=response),
            "amount_in_stock": self.parse_amounts_in_stock(response=response),
            "rating": self.parse_ratings(response=response),
            "category": self.parse_categories(response=response),
            "description": self.parse_descriptions(response=response),
            "upc": self.parse_upcs(response=response),
        }

    def parse_titles(self, response: Response) -> None | str:
        return response.css("h1::text").get()

    def parse_prices(self, response: Response) -> None | float:
        return float(response.css("p.price_color::text").get().replace("£", ""))

    def parse_amounts_in_stock(self, response: Response) -> None | int:
        return int(response.css("p.availability::text").re_first("\d+"))

    def parse_ratings(self, response: Response) -> None | int:
        return self.RATING[response.css("p.star-rating::attr(class)").re_first("star-rating (\w+)")]

    def parse_categories(self, response: Response) -> None | str:
        return response.css(".breadcrumb > li > a::text").getall()[-1]

    def parse_descriptions(self, response: Response) -> None | str:
        return response.css("#product_description + p::text").get()

    def parse_upcs(self, response: Response) -> None | str:
        return response.css("tr:contains('UPC') td::text").get()
