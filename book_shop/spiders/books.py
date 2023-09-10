import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: Response, **kwargs) -> None:
        books = response.css(".product_pod")

        for book in books:
            relative_url = book.css("h3 a").attrib["href"]
            book_url = response.urljoin(relative_url)
            yield scrapy.Request(book_url, callback=self.parse_book_page)

        next_page = response.css(".next a").attrib["href"]

        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    @staticmethod
    def parse_book_page(response: Response) -> None:
        table_rows = response.css("table tr")
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": response.css(".price_color::text").get(),
            "amount_in_stock": table_rows[5]
            .css("td::text")
            .get()
            .split()[2][1:],
            "rating": response.css(".star-rating").attrib["class"].split()[1],
            "category": response.xpath("//li[3]/a/text()").get(),
            "description": response.css("article > p::text").get(),
            "upc": table_rows[0].css("td::text").get(),
        }
