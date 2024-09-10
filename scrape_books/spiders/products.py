import scrapy
from scrapy.http import Response


TEXT_TO_NUMBER = {
    "Zero": 0,
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            url = book.css("h3 > a::attr(href)").get()

            if url is not None:
                book_url = response.urljoin(url)
                yield scrapy.Request(book_url, callback=self.parce_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parce_book(response: Response) -> dict:
        rating_text = response.css(
            ".star-rating::attr(class)"
        ).get().split()[-1]
        rating_number = TEXT_TO_NUMBER.get(rating_text, 0)

        book = {
            "title": response.css("h1::text").get(),
            "price": float(response.css(".price_color::text").get()[1:]),
            "amount_in_stock":
                response.css("p.availability::text").re_first(r"\d+"),
            "rating": rating_number,
            "category":
                response .css(".breadcrumb > li > a::text").getall()[-1],
            "description": response.css("article > p::text").get(),
            "UPC": response.css("tr > td::text").get(),
        }
        return book
