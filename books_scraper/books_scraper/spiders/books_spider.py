import scrapy
from books_scraper.items import BooksScraperItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: scrapy.http.Response)-> scrapy.http.Request:
        for book in response.css("article.product_pod h3 a::attr(href)"):
            yield response.follow(book, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: scrapy.http.Response) -> BooksScraperItem:
        item = BooksScraperItem()

        item["title"] = response.css("div.product_main h1::text").get()
        item["price"] =  float(response.css("p.price_color::text").get().replace("£", ""))
        item["amount_in_stock"] = int(response.css("p.instock.availability::text").re_first("\d+") or "0")
        item["rating"] = response.css("p.star-rating").attrib.get("class", "").split()[1]
        item["category"] = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        item["description"] = response.css("div#product_description + p::text").get()
        item["upc"] = response.css("table.table.table-striped tr:nth-child(1) td::text").get()

        yield item
