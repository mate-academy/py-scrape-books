import scrapy
from books_scraper.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books_scraper"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        # Extract links to individual book pages
        book_links = response.css("h3 a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, self.parse_book)

        # Follow pagination links to scrape additional pages
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response):
        item = BookItem()

        item["title"] = response.css("h1::text").get()
        item["price"] = response.css("p.price_color::text").get()
        item["amount_in_stock"] = response.css("p.instock.availability::text").re_first(
            r"\d+"
        )
        item["rating"] = response.css("p.star-rating::attr(class)").re_first(
            r"([a-zA-Z]+)"
        )
        item["category"] = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        item["description"] = response.css(
            'meta[name="description"]::attr(content)'
        ).get()
        item["upc"] = response.css("table.table-striped tr:nth-child(1) td::text").get()

        yield item
