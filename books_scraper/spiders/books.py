import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".col-lg-3"):
            yield {
                "tittle": book.css("h3 > a::attr(title)").get()
            }

        # next_page = response.css(".pager > li.next > a::attr(href)").get()
        next_page = response.css(".next > a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)
