import scrapy
from scrapy.http import Response
from word2number.w2n import word_to_num as w2n


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            detail_page_link = book.css("h3 a::attr(href)").get()
            if detail_page_link:
                yield response.follow(detail_page_link, self.parse_single_book)

        next_page = response.css(".pager .next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_single_book(self, response: Response) -> None:
        title = response.css("h1::text").get()
        price = float(response.css(
            ".price_color::text").get().replace("£", "")
        )
        amount_in_stock = int(response.css(
            ".instock.availability::text").re_first(r"\d+")
        )
        rating = w2n(response.css(
            ".star-rating::attr(class)").get().split()[1]
        )
        category = response.css(".breadcrumb li:nth-child(3) a::text").get()
        description = response.css("#product_description ~ p::text").get()
        upc = response.css("tr td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc
        }
