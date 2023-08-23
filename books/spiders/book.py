import scrapy
import subprocess
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            link = book.css("h3 > a::attr(href)").get()
            yield scrapy.Request(
                response.urljoin(link),
                callback=self.parse_single_book,
            )

        next_page = response.css("ul.pager li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_single_book(self, response: Response):
        page = response.css(".product_page")
        availability = response.xpath(
            '//tr[th[contains(text(), "Availability")]]'
        ).css("td::text").get()
        rating = page.css("p.star-rating::attr(class)").get()
        yield {
            "title": page.css("h1::text").get(),
            "price": page.css("p.price_color::text").get()[1:],
            "amount_in_stock": "".join(filter(str.isdigit, availability)),
            "rating": self.parse_rating(rating),
            "category": response.css(
                "ul.breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            "description": page.css(
                "div#product_description + p::text"
            ).get(),
            "upc": response.xpath(
                '//tr[th[contains(text(), "UPC")]]'
            ).css("td::text").get()
        }

    @staticmethod
    def parse_rating(rating: str) -> int:
        choice_rating = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        return choice_rating[rating.split()[1]]


def main() -> None:
    scrapy_command = ["scrapy", "crawl", "book", "-O", "books.jl"]
    subprocess.run(scrapy_command, capture_output=True, text=True)


if __name__ == "__main__":
    main()
