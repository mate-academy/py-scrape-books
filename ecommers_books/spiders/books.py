import scrapy
from scrapy.http import Response

RATING_DICT = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def start_requests(self) -> Response:
        urls = ["https://books.toscrape.com/"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.get_book_detail_page)

    def get_book_detail_page(self, response: Response) -> Response:
        for book in response.css(".product_pod"):
            book_detail = book.css("div > a::attr(href)").get()
            yield response.follow(book_detail, callback=self.parse)

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield response.follow(
                next_page_url, callback=self.get_book_detail_page
            )

    def parse(self, response: Response, **kwargs) -> dict:
        book_table = response.css("td::text").getall()
        yield dict(
            title=response.css("h1::text").get(),
            price=float(
                response.css("p.price_color::text").get().replace("£", "")
            ),
            amount_in_stock=int(
                "".join([char for char in book_table[5] if char.isnumeric()])
            ),
            rating=RATING_DICT.get(
                response.css("p.star-rating::attr(class)").get().split()[-1]
            ),
            category=response.css("ul.breadcrumb > li > a::text").getall()[2],
            description=max(response.css("p").getall()).replace(
                "<p>", ""
            ).replace(
                "</p>", ""
            ),
            upc=book_table[0]
        )
