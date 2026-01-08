import scrapy
from ..items import BookItem  # Import the item we defined above

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        """
        Step 1: Parse the catalogue page.
        - Find links to individual book pages.
        - specific book data is NOT extracted here because description/UPC
          are only available on the detail page.
        - Handle pagination to the next page.
        """
        # Select all book links on the current page
        book_links = response.css("article.product_pod h3 a::attr(href)")

        for link in book_links:
            # Follow the link to the book's detail page
            yield response.follow(link, callback=self.parse_book)

        # Find the 'Next' button and follow it if it exists
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        """
        Step 2: Parse the book detail page.
        - Extract all required fields.
        - Clean the data.
        - Yield the final item.
        """
        item = BookItem()

        # 1. Title
        item["title"] = response.css("div.product_main h1::text").get()

        # 2. Price
        # Extract raw text (e.g., "£51.77") and keep it simple
        item["price"] = response.css("p.price_color::text").get()

        # 3. Amount in stock
        # Text is usually "In stock (22 available)". 
        # We strip whitespace to make it clean.
        raw_stock = response.css("p.instock.availability::text").re_first(r'\S.*')
        if raw_stock:
             # Extract just the number using regex if needed, or keep full text.
             # Based on "amount_in_stock", usually an integer is preferred:
             stock_count = response.css("p.instock.availability::text").re_first(r'\((\d+)\s+available\)')
             item["amount_in_stock"] = int(stock_count) if stock_count else 0

        # 4. Rating
        # The rating is stored as a class name: "star-rating Three"
        # We can map the word to a number.
        rating_classes = response.css("p.star-rating::attr(class)").get()
        item["rating"] = self.convert_rating(rating_classes)

        # 5. Category
        # Usually found in the breadcrumb navigation (3rd link)
        # Home > Books > Category > Title
        category_list = response.xpath("//ul[@class='breadcrumb']/li/a/text()").getall()
        # The category is usually the last link in the breadcrumbs (index -1)
        item["category"] = category_list[-1] if category_list else None

        # 6. Description
        # It is the paragraph immediately following the #product_description div
        item["description"] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()

        # 7. UPC
        # Found in the table at the bottom
        item["upc"] = response.xpath("//th[text()='UPC']/following-sibling::td/text()").get()

        yield item

    def convert_rating(self, rating_class):
        """Helper to convert text rating to integer"""
        if not rating_class:
            return 0

        rating_map = {
            'One': 1,
            'Two': 2,
            'Three': 3,
            'Four': 4,
            'Five': 5
        }

        # Split "star-rating Three" and find the number word
        parts = rating_class.split()
        for part in parts:
            if part in rating_map:
                return rating_map[part]
        return 0
