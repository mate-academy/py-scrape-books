import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags


class BookItem(scrapy.Item):
    title = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())
    stock = scrapy.Field(output_processor=TakeFirst())
    rating = scrapy.Field(output_processor=TakeFirst())
    category = scrapy.Field(output_processor=TakeFirst())
    description = scrapy.Field(
        input_processor=MapCompose(remove_tags), output_processor=TakeFirst()
    )
    upc = scrapy.Field(output_processor=TakeFirst())


class BooksToScrapeSpider(scrapy.Spider):
    name = "books_to_scrape"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    def parse(self, response):
        book_links = response.css("h3 a::attr(href)").getall()
        for book_link in book_links:
            yield response.follow(book_link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color::text").extract_first(),
            "amount_in_stock": response.css("p.instock.availability").re_first(r"\d+"),
            "rating": response.css("p.star-rating::attr(class)").re_first(
                r"One|Two|Three|Four|Five"
            ),
            "category": response.css(
                "ul.breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            "description": response.css("meta[name=description]::attr(content)").get(),
            "upc": response.css("th:contains('UPC') + td::text").get(),
        }
