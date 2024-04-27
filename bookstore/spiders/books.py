import scrapy
from scrapy.http import Response
from bookstore.items import Book

# Define rating map as a constant
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) -> scrapy.Request:
        book_detail_links = response.css(".product_pod > h3 > a::attr(href)").getall()

        for link in book_detail_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _get_amount_in_stock(response: Response) -> int:
        stock_text = response.css("table.table td::text").getall()
        print("Stock text:", stock_text)
        if len(stock_text) >= 6:
            stock_quantity_text = stock_text[5]
            stock_quantity = "".join(filter(str.isdigit, stock_quantity_text))
            print("Stock quantity:", stock_quantity)
            if stock_quantity:
                return int(stock_quantity)

        return 0

    @staticmethod
    def _get_rating(response: Response) -> int:
        rating_classes = response.css("p.star-rating::attr(class)").get()
        return RATING_MAP.get(rating_classes.split()[1])

    def parse_book(self, response: Response) -> Book:
        yield Book(
            title=response.css(".product_main > h1::text").get(),
            price=float(response.css("p.price_color::text").get().replace("£", "")),
            amount_in_stock=self._get_amount_in_stock(response),
            rating=self._get_rating(response),
            category=response.css(".breadcrumb > li > a::text").getall()[-1],
            description=response.css(".product_page > p::text").get(),
            upc=response.css("table.table-striped td::text").get(),
        )
