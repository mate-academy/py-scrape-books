import scrapy
from scrapy.http import Response


class MySpiderSpider(scrapy.Spider):
    name = "my_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) -> scrapy.Request:
        for book in response.css("h3 a"):
            book_url = response.urljoin(book.attrib["href"])
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(response.urljoin(next_page), callback=self.parse)

    def parse_book(self, response: Response) -> dict:
        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css("p.price_color::text").get().replace("£", "")),
            "amount_in_stock": int(
                response.css("p.instock.availability::text").re_first(r"\d+")
            ),
            "rating": response.css("p.star-rating").attrib["class"].split()[-1],
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("meta[name='description']::attr(content)")
            .get()
            .strip(),
            "upc": response.css("table tr:nth-child(1) td::text").get(),
        }
