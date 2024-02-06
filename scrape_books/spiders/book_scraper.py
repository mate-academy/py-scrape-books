import scrapy
from scrapy import Selector

STARS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class BookScraperSpider(scrapy.Spider):
    name = "book_scraper"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        product_links = response.css(".product_pod a::attr(href)").getall()
        for product_link in product_links:
            yield scrapy.Request(
                url=response.urljoin(product_link),
                callback=self.parse_products
            )

        next_page_link = response.css(".next a::attr(href)").get()
        if next_page_link is not None:
            yield response.follow(next_page_link, callback=self.parse)

    @staticmethod
    def get_digits(string):
        number = ""
        for symbol in string:
            if symbol.isdigit():
                number += symbol
        return int(number) if number else None

    @staticmethod
    def find_data_in_table(response, th_name: str) -> str:
        table = response.xpath('//*[@class="table table-striped"]')
        rows = table.xpath('//tr')
        for row in rows:
            if row.xpath('th//text()')[0].extract() == th_name:
                return row.xpath('td//text()')[0].extract()
        return "Not found"

    def parse_products(self, response, **kwargs):
        title = response.css(".product_main h1::text").get()
        price = response.css(".price_color::text").get()[1:]
        amount_in_stock = self.find_data_in_table(response, "Availability")
        UPC = self.find_data_in_table(response, "UPC")
        star_rating = response.css(".star-rating").css('::attr(class)').get().split()[1]
        description = response.css("p:not([class])::text").get()
        breadcrumbs = response.css(".breadcrumb li").getall()
        category = Selector(text=breadcrumbs[2]).css("a::text").get()
        yield {
            "title": title,
            "price": price,
            "amount_in_stock": self.get_digits(amount_in_stock),
            "star_rating": STARS[star_rating],
            "category": category,
            "description": description,
            "UPC": UPC
        }
