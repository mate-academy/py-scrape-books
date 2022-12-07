import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        list_books = response.css(".product_pod")
        for book in list_books:
            detail_page = book.css("a::attr(href)").get()
            if detail_page is not None:
                yield response.follow(detail_page, self.parse_detail_page)
        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, self.parse)

    @staticmethod
    def parse_detail_page(book, **kwargs):
        rating_enum = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        yield {
            "title": book.css("h1::text").get(),
            "price": float(book.css(".price_color::text").get()[1:]),
            "amount_in_stock": int(book.css(".availability::text").getall()[1].split("(")[1].split()[0]),
            "rating": rating_enum.get(book.css(".star-rating::attr(class)").get().split()[-1], 0),
            "category": book.css(".breadcrumb").css("li")[-2].css("a::text").get(),
            "description": book.xpath("//p[contains(., '...more')]").css("p::text").get(),
            "upc": book.css(".table-striped > tr > td::text").get()
        }
