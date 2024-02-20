import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        book_page_links = response.css(".product_pod > h3 > a")
        yield from response.follow_all(book_page_links, self.parse_book)

        next_page = response.css(".next > a::attr(href)").get()

        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_book(self, response):
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                response.css(".table > tr")[-2].css("td::text").get().split()[2][1:]
            ),
            "rating": response.css(".star-rating::attr(class)").get().split()[-1],
            "category": response.css(".breadcrumb > li > a::text")[-1].get(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table > tr")[0].css("td::text").get(),
        }
