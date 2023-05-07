import scrapy
from scrapy.http import Response


class AuthorSpider(scrapy.Spider):
    name = "books"

    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        book_page_links = response.css(".image_container a::attr(href)")
        yield from response.follow_all(book_page_links, parse_book)

        pagination_links = response.css('li.next a')
        yield from response.follow_all(pagination_links, self.parse)


def parse_book(response):
    def extract_with_css(query):
        return response.css(query).get(default='').strip()

    yield {
        "title": extract_with_css("a::attr(title)"),
        "price": float(extract_with_css("p.price_color::text").replace("£", "")),
        "amount_in_stock": int(response.css(".availability").get().split()[7].replace("(", "")),
        "rating": response.css('.star-rating').xpath("@class").get().split(" ")[1],
        "category": response.css(".breadcrumb > li > a").getall()[-1].split(">")[-2].replace("</a", ""),
        "description": response.css(".sub-header + p::text").get(),
        "UPC": response.css(".table > tr > td::text").get(),
    }
