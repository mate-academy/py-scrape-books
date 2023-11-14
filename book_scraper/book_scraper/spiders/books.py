import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def get_rating(text: str) -> int:
        number_str = text.split()[-1]
        number_dict = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        return number_dict.get(number_str, 0)

    def parse(self, response: Response) -> str:
        for book in response.css(".product_pod"):
            detail_page = response.urljoin(
                book.css("h3 > a::attr(href)"
                         ).get())
            yield scrapy.Request(detail_page, callback=self.parse_book_detail)

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_book_detail(self, response: Response) -> dict:
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(response.css(
                ".price_color::text"
            ).get().replace("£", "")),
            "amount_in_stock": int(response.css(
                ".instock"
            ).get().split()[-3][1:]),
            "rating": self.get_rating(response.css(
                "p.star-rating::attr(class)"
            ).get()),
            "category": response.css(
                ".breadcrumb li:nth-child(3) a::text"
            ).get(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table td::text").get(),
        }

    def start_requests(self) -> str:
        yield scrapy.Request(
            url=self.start_urls[0],
            callback=self.parse_total_pages
        )

    def parse_total_pages(self, response: Response) -> str:
        num_pages_text = response.css("li.current").xpath("text()").get()
        num_pages = int("".join(filter(str.isdigit, num_pages_text)))
        for i in range(1, num_pages + 1):
            yield scrapy.Request(
                url=f"https://books.toscrape.com/catalogue/page-"
                f"{i}.html", callback=self.parse
            )

    def closed(self, reason: str) -> None:
        self.log(f"Scraped "
                 f"{self.crawler.stats.get_value('item_scraped_count')} "
                 f"books.")
