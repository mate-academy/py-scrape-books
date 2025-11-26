import scrapy
from scrapy.http import Response


def parse_book_info(response: Response):
    yield {
        "title": response.css(".product_main h1::text").get(),
        "price": response.css(".price_color::text").get().replace("£", ""),
        "amount_in_stock": response.css(".instock.availability::text")
                               .re_first(r'\d+') or "0",
        "rating": response.css("p.star-rating::attr(class)")
                          .get()
                          .replace("star-rating", "")
                          .strip(),
        "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
        "description": response.css("#product_description ~ p::text").get(),
        "upc": response.css("table tr:nth-child(1) td::text").get()
    }


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs):
        for book in response.css("article.product_pod"):
            book_link = book.css("h3 a::attr(href)").get()
            absolute_url = response.urljoin(book_link)

            yield scrapy.Request(
                url=absolute_url,
                callback=parse_book_info
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
