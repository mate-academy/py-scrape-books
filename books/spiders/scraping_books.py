import scrapy
from scrapy.http import Response

NUM_RATING = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class ScrapingBooksSpider(scrapy.Spider):
    name = "scraping_books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:

        books = response.css("h3 a::attr(href)").getall()
        for book in books:
            yield response.follow(book, callback=self._parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_book(self, response: Response) -> None:

        title = response.css("h1::text").get()
        price = float(response.css(".price_color::text").get().replace("£", ""))
        stock = int(response.css("p.instock.availability::text").re_first(r"\d+"))
        rating = response.css("p.star-rating::attr(class)").re_first(
            r"star-rating (.+)"
        )
        category = response.css("ul.breadcrumb li:nth-last-child(2) a::text").get()
        description = response.css("div#product_description + p::text").get()
        upc = response.css('th:contains("UPC") + td::text').get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": stock,
            "rating": NUM_RATING[rating],
            "category": category,
            "description": description,
            "upc": upc,
        }
