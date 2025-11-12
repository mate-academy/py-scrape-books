import scrapy

from library_scraper.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    custom_settings = {
        "FEEDS": {
            "books.jl": {
                "format": "jsonlines",
                "encoding": "utf8",
                "overwrite": True,
            },
        },
    }

    def parse(self, response):
        """Parse the main page and follow pagination"""
        # Extract all book links on current page
        books = response.css("article.product_pod h3 a::attr(href)").getall()

        for book_url in books:
            yield response.follow(book_url, callback=self.parse_book)

        # Follow pagination
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        """Parse individual book page"""
        book = BookItem()

        book["title"] = response.css("div.product_main h1::text").get()

        price_text = response.css("p.price_color::text").get()
        book["price"] = price_text.replace("£", "") if price_text else ""

        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating_class = response.css("p.star-rating::attr(class)").get()
        rating_text = rating_class.split()[-1] if rating_class else None
        book["rating"] = rating_map.get(rating_text, 0)

        availability_text = response.css("p.instock.availability::text").getall()
        availability_text = "".join(availability_text).strip()

        amount_in_stock = 0
        if "(" in availability_text and "available" in availability_text:
            amount_str = availability_text.split("(")[1].split(" ")[0]
            try:
                amount_in_stock = int(amount_str)
            except ValueError:
                amount_in_stock = 0
        book["amount_in_stock"] = amount_in_stock

        book["category"] = response.css("ul.breadcrumb li:nth-child(3) a::text").get()

        description_elem = response.css("div#product_description + p::text").get()
        book["description"] = description_elem.strip() if description_elem else ""

        upc = ""
        for row in response.css("table.table.table-striped tr"):
            key = row.css("th::text").get()
            value = row.css("td::text").get()
            if key == "UPC":
                upc = value
                break
        book["upc"] = upc

        yield book
