import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            title = book.css("h3 a::attr(title)").get()
            price = book.css("p.price_color::text").get().replace("£", "")
            rating = book.css(".star-rating::attr(class)").get().split()[-1]
            book_url = book.css("h3 a::attr(href)").get()
            yield response.follow(
                book_url,
                callback=self.parse_book,
                meta={"title": title, "price": price, "rating": rating},
            )
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response):
        title = response.meta["title"]
        price = response.meta["price"]
        rating = response.meta["rating"]

        description = response.css("#product_description ~ p::text").get()
        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        availability = response.css(".availability::text").re_first(r"\d+")
        upc = response.css("th:contains('UPC') + td::text").get()

        yield {
            "title": title,
            "price": price,
            "rating": rating,
            "category": category,
            "amount_in_stock": availability,
            "upc": upc,
            "description": description,
        }
