import scrapy
from scrapy.http import Response


RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5
}


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        books = response.css("div ol.row li")
        for book in books:
            detailed_url = response.urljoin(book.css("h3 a::attr(href)").get())
            yield scrapy.Request(detailed_url,
                                 callback=self._parse_book_detail)

        next_page = response.css("ul.pager li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _parse_book_detail(response: Response) -> dict[str, str]:
        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css(
                "p.price_color::text"
            ).get().replace("£", "")),
            "amount_in_stock": int(response.css(
                ".table.table-striped tr td::text"
            ).getall()[-2].split()[-2].replace("(", "")),
            "rating": RATING_MAP[response.css(
                "p.star-rating::attr(class)"
            ).get().split()[1].lower()],
            "category": response.css(".breadcrumb li a::text")[2].get(),
            "description": response.css(
                "article.product_page > p::text"
            ).get(),
            "upc": response.css(
                ".table.table-striped tr td::text"
            ).getall()[0],
        }
