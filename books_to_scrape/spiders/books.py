import scrapy
from scrapy.http import Response


LITERAL_TO_NUMERAL_RATING = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs) -> None:
        for url in response.css(".product_pod > h3 > a::attr(href)").getall():
            yield scrapy.Request(
                url=response.urljoin(url), callback=self.parse_book_detail
            )

        next_page = response.css(".next").css("a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    @staticmethod
    def parse_book_detail(response: Response, **kwargs) -> dict:
        title = response.css(".product_main > h1::text").get()
        price = float(response.css(".price_color::text").get().replace(
            "£", ""
        ))
        raw_availability = response.xpath(
            "//th[contains(text(), 'Availability')]"
            "/following-sibling::td/text()"
        ).get()
        amount_in_stock = int(raw_availability[raw_availability.index(
            "("
        ) + 1:].split()[0])
        rating = response.css(".star-rating::attr(class)").get().split()[-1]
        rating = LITERAL_TO_NUMERAL_RATING[rating]
        category = response.css(
            "ul.breadcrumb li:nth-last-child(2) a::text"
        ).get()
        description = response.css(".product_page > p::text").get()
        upc = response.xpath(
            '//th[contains(text(), "UPC")]/following-sibling::td/text()'
        ).get()
        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "upc": upc,
            "description": description
        }
