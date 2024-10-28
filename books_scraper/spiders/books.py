import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]

    @staticmethod
    def parse_detail_info_from_book(response: Response):
        ratings = {
            "One": "1",
            "Two": "2",
            "Three": "3",
            "Four": "4",
            "Five": "5"
        }
        available_text = " ".join(
            response.css("p.instock.availability::text").getall()).strip()
        available = ""

        for i in available_text:
            if i.isdigit():
                available += i

        rating_word = response.css(
            "p.star-rating::attr(class)"
        ).get().split()[-1]
        rating = ratings.get(rating_word, 0)

        yield {
            "title": response.css("h1::text").get(),
            "price": response.css(".price_color::text").get().replace("£", ""),
            "amount_in_stock": available if len(available) > 0 else "0",
            "rating": rating,
            "category": response.css(
                ".breadcrumb > li:nth-last-child(2) a::text"
            ).get(),
            "description": response.css(
                ".product_page > p::text"
            ).get()[:-7] or "No description",
            "upc": response.css(
                ".table.table-striped > tr:nth-child(1) td::text"
            ).get() or "No upc"

        }

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            detailed_url = response.urljoin(
                book.css(
                    "h3 > a::attr(href)"
                ).get())
            yield response.follow(
                detailed_url,
                callback=self.parse_detail_info_from_book
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse
            )
