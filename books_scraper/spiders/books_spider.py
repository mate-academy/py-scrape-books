import scrapy

from books_scraper.items import BookItem

RATINGS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        category_links = response.css(
            ".side_categories ul li ul li a::attr(href)"
        ).getall()
        for link in category_links:
            yield response.follow(link, callback=self.parse_category)

    def parse_category(self, response):
        book_links = response.css("article.product_pod h3 a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_category)

    def parse_book(self, response):
        table_data = {
            row.css("th::text").get(): row.css("td::text").get()
            for row in response.css("table.table.table-striped tr")
        }

        category = response.css(".breadcrumb li a::text").getall()[-1]

        rating_class = response.css("p.star-rating::attr(class)").get()
        rating_word = rating_class.replace("star-rating", "").strip()

        yield BookItem(
            title=response.css("div.product_main h1::text").get(),
            price=float(table_data["Price (incl. tax)"].replace("£", "")),
            amount_in_stock=self.parse_stock(table_data["Availability"]),
            rating=RATINGS.get(rating_word, 0),
            category=category,
            description=self.parse_description(response),
            upc=table_data["UPC"],
        )

    @staticmethod
    def parse_stock(availability_text):
        digits = "".join(char for char in availability_text if char.isdigit())
        return int(digits) if digits else 0

    @staticmethod
    def parse_description(response):
        description = response.css("#product_description + p::text").get()
        return description.strip() if description else ""
