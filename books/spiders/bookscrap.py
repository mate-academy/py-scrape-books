import scrapy
from scrapy.http import Response


class BookscrapSpider(scrapy.Spider):
    name = "bookscrap"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def parse_books(book: Response) -> dict:
        yield {
         "title": book.css(".product_main > h1::text").get(),
         "price": book.css(".price_color::text").get().replace("£", ""),
         "amount_in_stock": int(book.css(".instock.availability").get().split()[-3][1:]),
         "rating": book.css("p.star-rating::attr(class)").get().split()[-1],
         "category": book.css("li:nth-child(3) a::text").get(),
         "description": book.css("article > p::text").get(),
         "upc": book.css(".table tr td::text").get()
        }

    def parse(self, response: Response, **kwargs):
        for page in response.css(".product_pod").css("h3 a::attr(href)"):
            yield scrapy.Request(
                response.urljoin(page.get()), callback=self.parse_books
                )
        next_page = response.css("li.next a::attr(href)").get()

        if next_page is not None:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, callback=self.parse)
