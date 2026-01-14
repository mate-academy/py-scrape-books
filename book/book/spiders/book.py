import scrapy


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/"]

    async def start(self):
        for url in self.start_urls:
            for index in range(1, 51):
                yield scrapy.Request(f"{url}/page-{index}.html")

    def parse(self, response):
        book_links = response.css("article.product_pod a::attr(href)").getall()
        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

    def parse_book(self, response):
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css("p.price_color::text").get().replace("£", ""),
            "amount_in_stock": response.css("tr:nth-child(6) td::text").get(),
            "rating": response.css("p.star-rating").xpath("@class").extract()[0].split(" ")[1],
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css("article > p::text").get(),
            "upc": response.css("tr:nth-child(1) td::text").get()
        }