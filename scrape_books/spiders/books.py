import scrapy
from scrapy.http import Response
from scrape_books.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            rating_class = book.css(
                ".star-rating::attr(class)"
            ).get().split()[-1]

            book_item = BookItem(
                title=book.css("h3 a::attr(title)").get(),
                price=float(book.css(
                    ".product_price .price_color::text"
                ).get().replace("£", "")),
                rating=self.rating_map.get(rating_class, 0)
            )

            yield response.follow(
                book.css("h3 a::attr(href)").get(),
                callback=self.parse_book_details,
                cb_kwargs={"book_item": book_item}
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(
            self,
            response: Response,
            book_item: BookItem
    ) -> None:
        book_item.amount_in_stock = int(response.css(
            "th:contains('Availability') + td::text"
        ).get().split("(")[-1].split(" ")[0])
        book_item.description = response.css(
            "#product_description + p::text").get()
        book_item.upc = response.css("th:contains('UPC') + td::text").get()

        yield book_item
