import scrapy
from books_scraper.books_scraper.items import BooksScraperItem


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["http://books.toscrape.com/"]

    def parse(self, response):
        for book_url in response.css("h3 a::attr(href)").getall():
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response):
        item = BooksScraperItem()

        item["title"] = response.css(".product_main h1::text").get()
        item["price"] = response.css(".price_color::text").get()
        item["amount_in_stock"] = response.css(".availability::text").re_first(r'\d+')
        item["rating"] = response.css(".star-rating::attr(class)").re_first("star-rating (\w+)")
        item["category"] = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        item["description"] = response.css("#product_description ~ p::text").get()
        item["upc"] = response.css("table.table-striped tr:nth-child(1) td::text").get()

        yield item
