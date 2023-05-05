import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    custom_settings = {
        "FEED_FORMAT": "jsonlines",
        "FEED_URI": "books.jl",
    }

    def parse(self, response: Response, **kwargs) -> None:
        book_urls = response.css(".product_pod a")
        yield from response.follow_all(book_urls, self.parse_book)
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> None:
        rating_elem = response.css("p.star-rating")[0]
        rating = rating_elem.attrib["class"].split()[-1]
        ratings = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": float(
                response.css(
                    ".product_main .price_color::text"
                ).get().replace("£", "")
            ),
            "amount_in_stock": int(
                "".join(
                    filter(
                        str.isdigit,
                        response.css("tr")[-2].css("td::text").get()
                    )
                )
            ),
            "rating": ratings[rating],
            "category": response.css(
                ".breadcrumb li"
            )[-2].css("a::text").get(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css("tr")[0].css("td::text").get()
        }
