import scrapy


class BooksScrapeSpider(scrapy.Spider):
    name = "books_scrape"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        for book in response.css("article.product_pod"):
            yield {
                "title": book.css("h3 a::attr(title)").get(),
                "price": book.css(".price_color::text").get(),
                "amount_in_stock": book.css(".instock.availability::text")
                .get()
                .strip(),
                "rating": book.css("p.star-rating::attr(class)").re_first(
                    "star-rating ([A-Za-z]+)"
                ),
                "category": book.css("a[title]::text").get(),
                "description": book.css("p::text").get(),
                "upc": book.css(".product_code::text").get(),
            }

        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
