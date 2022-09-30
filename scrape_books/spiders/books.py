from urllib.parse import urljoin

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def get_urls_for_all_books_in_page(response: Response):
        return [
            url.css(".image_container > a ::attr(href)").get()
            for url in response.css(".col-xs-6")
        ]

    @staticmethod
    def get_correct_upc(upc: str):
        return upc.split("td")[-2].replace("<", "").replace(">", "").replace("/", "")

    @staticmethod
    def get_correct_amount_in_stock(amount_in_stock: str):
        return (
            amount_in_stock.split("\n")[-3].strip().split()[-2].replace("(", "")
            + " available"
        )

    @staticmethod
    def get_correct_rating(rating: str):
        return rating.split("\n")[0].split()[-1][0:-2]

    def get_info_about_single_book(self, response: Response):
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color:nth-child(2)::text").get(),
            "amount_in_stock": self.get_correct_amount_in_stock(
                response.css(".instock").get()
            ),
            "rating": self.get_correct_rating(response.css(".star-rating").get()),
            "category": response.css(
                ".breadcrumb > li:nth-child(3) > a:nth-child(1)::text"
            ).get(),
            "descriptions": response.css(".product_page > p:nth-child(3)::text").get(),
            "upc": self.get_correct_upc(response.css(".table > tr:nth-child(1)").get()),
        }

    def parse(self, response: Response, **kwargs):
        all_urls = self.get_urls_for_all_books_in_page(response)

        for url in all_urls:
            book_url = urljoin(self.start_urls[0], url)

            yield scrapy.Request(book_url, callback=self.get_info_about_single_book)

        next_page = response.css(".next > a:nth-child(1)::attr(href)").get()

        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)