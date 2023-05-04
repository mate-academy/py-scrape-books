import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def parse_book_page(book_page: Response):
        title = book_page.css(".product_main > h1::text").get()
        price = "".join(
            book_page.css(".product_main > p.price_color::text").extract()
        ).strip()
        amount_in_stock = (
            book_page.css(".product_main > p.availability::text")
            .getall()[1]
            .strip()
            .split()[2][1:]
        )
        rating = (
            book_page.css(".product_main > p.star-rating::attr(class)")
            .get()
            .split(" ")[-1]
        )
        category = book_page.css(".breadcrumb > li > a::text").getall()[-1]
        description = book_page.css("article.product_page > p::text").get()
        upc = book_page.css("table tr td::text").get()
        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }

    def parse(self, response: Response, **kwargs):
        for book in response.xpath('//article[@class="product_pod"]'):
            link = book.xpath(".//a/@href").extract_first()
            yield scrapy.Request(
                url=response.urljoin(link), callback=self.parse_book_page
            )

        next_page_url = response.css("li.next a::attr(href)").extract_first()
        if next_page_url:
            yield scrapy.Request(
                url=response.urljoin(next_page_url), callback=self.parse
            )
