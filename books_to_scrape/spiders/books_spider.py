import scrapy
import wordtodigits
from scrapy.http import Response


class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        detail_links = response.css(".product_pod h3 a::attr(href)").getall()
        for link in detail_links:
            yield response.follow(link, callback=self.parse_detail)
        next_page = response.css(".pager > li:last-child a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_detail(self, response: Response) -> None:
        rating = response.css("p.star-rating::attr(class)").get().split()[1]

        yield {
            "title": response.css("h1::text").get(),
            "price": float(response.css(".price_color::text").get().replace("£", "")),
            "amount_in_stock": int(
                response.xpath("normalize-space(//p[@class='instock availability'])")
                .get()
                .replace("(", "")
                .split()[2]
            ),
            "rating": int(wordtodigits.convert(rating)),
            "category": response.css(".breadcrumb li a::text")[-1].get(),
            "description": response.css("div+p::text").get(),
            "upc": response.css(".table tr td::text")[0].get(),
        }
