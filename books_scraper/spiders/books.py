import scrapy
from scrapy import Request
from scrapy.http import Response
from tqdm import tqdm
from word2number.w2n import word_to_num

from books_scraper.items import BookItem


class BooksSpider(scrapy.Spider):
    """Spider for scraping books from books.toscrape.com website."""

    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs) -> None:
        """Initialize spider with progress bar."""
        super().__init__(*args, **kwargs)
        self.progress_bar = None
        self.books_count = 0

    def parse(self, response: Response, **kwargs: dict) -> Request:
        """Parse main page and follow links to book pages."""
        if not self.progress_bar:
            total_books = int(
                response.css("form.form-horizontal strong::text").get()
            )
            self.progress_bar = tqdm(
                total=total_books,
                desc="Scraping books",
                colour="green",
                unit="book",
            )

        book_links = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()

        for book_link in book_links:
            yield response.follow(book_link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> BookItem:
        """Parse individual book page."""
        title = response.css("div.product_main h1::text").get()
        price = response.css("p.price_color::text").get().replace("£", "")

        stock_text = (
            response.css("p.instock.availability::text").getall()[1].strip()
        )
        amount_in_stock = int(stock_text.split("(")[1].split()[0])

        rating_class = response.css("p.star-rating::attr(class)").get()
        rating = word_to_num(rating_class.split()[-1].lower())

        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        description = response.css("#product_description + p::text").get()
        upc = response.css(
            "table.table-striped tr:nth-child(1) td::text"
        ).get()

        book = BookItem(
            title, price, amount_in_stock, rating, category, description, upc
        )
        self.progress_bar.update(1)

        yield book

    def closed(self, reason: str) -> None:
        """Called when spider is closed."""
        self.progress_bar.close()

        self.logger.info(f"Spider closed: {reason}")
