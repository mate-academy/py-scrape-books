import scrapy
from scrapy.http import Response


class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:

        for book in response.css(".product_pod"):
            detail_url = response.urljoin(book.css("h3 > a::attr(href)").get())
            yield scrapy.Request(detail_url, callback=self.parse_book_details)

        next_page = response.css(".pager > li")[-1].css("a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    @staticmethod
    def parse_book_details(response: Response) -> None:
        title = response.css(".product_main h1::text").get()
        price = float(
            response.css(".price_color::text").get().replace("£", "")
        )
        category = response.css(".breadcrumb li:nth-child(3) a::text").get()
        description = response.css(".sub-header + p::text").get()
        upc = response.css(
            "table.table-striped tr:nth-child(1) td::text"
        ).get().strip()

        stock_text = response.css(".availability::text").getall()
        amount_is_stock = int("".join(stock_text).split()[2][1:])

        num_rating = ["One", "Two", "Three", "Four", "Five"]
        rating_word = response.css(
            ".star-rating::attr(class)"
        ).get().split()[-1]
        rating = num_rating.index(rating_word) + 1

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_is_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
