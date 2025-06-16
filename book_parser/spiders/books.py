import scrapy
from book_parser.items import BooksParserItem

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    rating_map = {
        "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5,
    }

    def parse(self, response, **kwargs):
        for link in response.css(".product_pod h3 > a::attr(href)").getall():
            yield response.follow(link, self.parse_book_page)
        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book_page(self, response):
        yield BooksParserItem(
            title=response.css(".product_main > h1::text").get(),
            price=float(response.css(".price_color::text").get().replace("£", "")),
            amount_in_stock=int(response.css(".instock").re_first(r"\d+")),
            rating=self.rating_map[response.css(".star-rating::attr(class)").get().split()[-1]],
            category=response.css(".breadcrumb > li > a::text")[-2].get(),
            description=response.css("#product_description + p::text").get(),
            upc=response.css(".table tr td::text").get(),
        )