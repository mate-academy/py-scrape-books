import scrapy
from books_scraper.items import BooksScraperItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    def parse(self, response):
        """
        Step 1: Traverse the catalogue list pages, follow individual
        book page targets, and loop safely across pagination.
        """
        book_links = response.css("article.product_pod h3 a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book_details)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(self, response):
        """
        Step 2: Collect book metrics, resolve layout mismatches, and apply normalization rules.
        """
        def get_table_value(label):
            return response.xpath(f"//th[text()='{label}']/following-sibling::td/text()").get()

        rating_classes = response.css("p.star-rating::attr(class)").get("").split()
        text_rating = next((cls for cls in rating_classes if cls != "star-rating"), None)
        rating = self.RATING_MAP.get(text_rating, 0)

        stock_text = response.css("p.availability::text").getall()
        stock_cleaned = "".join(stock_text).strip()
        amount_in_stock = int("".join(filter(str.isdigit, stock_cleaned))) if any(c.isdigit() for c in stock_cleaned) else 0

        raw_price = response.css("p.price_color::text").get()
        price = 0.0
        if raw_price:
            price_digits = "".join(c for c in raw_price if c.isdigit() or c == ".")
            price = float(price_digits) if price_digits else 0.0

        raw_description = response.css("#product_description + p::text").get()
        description = raw_description.strip() if raw_description else ""

        yield BooksScraperItem(
            title=response.css("div.product_main h1::text").get(),
            price=price,
            amount_in_stock=amount_in_stock,
            rating=rating,
            category=response.css("ul.breadcrumb li:nth-last-child(2) a::text").get(),
            description=description,
            upc=get_table_value("UPC")
        )
