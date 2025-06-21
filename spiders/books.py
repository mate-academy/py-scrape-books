import scrapy
from scrapy.http import Response
from books_project.items import BooksProjectItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    NUMBERS = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.book_links = {}

    def parse(self, response: Response, **kwargs) -> None:
        self._get_books_links(response)

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        else:
            yield from self._parse_books()

    def _get_books_links(self, response: Response) -> None:
        for book in response.css(".product_pod"):
            title = book.css("h3 a::attr(title)").get()
            link = book.css("h3 a::attr(href)").get()
            if title and link:
                self.book_links[title] = response.urljoin(link)

    def _parse_books(self):
        for title, link in self.book_links.items():
            yield scrapy.Request(
                url=link,
                callback=self._parse_book,
                meta={"title": title}
            )

    def _parse_book(self, response: Response):
        rating_text = response.css("p.star-rating::attr(class)").get()
        rating = next(
            (
                self.NUMBERS[word]
                for word in self.NUMBERS
                if word in rating_text
            ),
            None
        )

        yield BooksProjectItem(
            title=response.css(".product_main h1::text").get(),
            price=response.css(".price_color::text").get(),
            amount_in_stock=response.css(".availability::text").re_first(r"\d+"),
            rating=rating,
            category=response.css(".breadcrumb li:nth-child(3) a::text").get(),
            description=response.css("#product_description ~ p::text").get(),
            upc=response.css("table tr:nth-child(1) td::text").get(),
        )
