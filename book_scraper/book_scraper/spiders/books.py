import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]

    def parse(self, response):
        book_links = response.css("h3 a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book_details)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(self, response):

        rating_mapping = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        raw_rating = response.css("p.star-rating::attr(class)").get()
        rating_word = raw_rating.replace("star-rating", "").strip() if raw_rating else None
        rating = rating_mapping.get(rating_word, 0)

        upc = response.xpath("//th[text()='UPC']/following-sibling::td/text()").get()
        price = response.xpath("//th[text()='Price (incl. tax)']/following-sibling::td/text()").get()

        stock_text = response.xpath("//th[text()='Availability']/following-sibling::td/text()").get()
        amount_in_stock = 0
        if stock_text and "(" in stock_text:
            amount_in_stock = int("".join(filter(str.isdigit, stock_text)))

        yield {
            "title": response.css("h1::text").get(),
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": response.css(".breadcrumb li:nth-last-child(2) a::text").get(),
            "description": response.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
            "upc": upc,
        }
