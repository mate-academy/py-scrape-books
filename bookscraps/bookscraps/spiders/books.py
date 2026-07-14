import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        for book_link in response.css("article.product_pod h3 a::attr(href)"):
            yield response.follow(book_link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        yield {
            "title": response.css("h1::text").get(),
            "price": response.css(".price_color::text").get(),
            "amount_in_stock": response.css(
                ".instock.availability::text"
            ).re_first(r"\d+"),
            "rating": response.css(
                "p.star-rating::attr(class)"
            ).get().split()[-1],
            "category": response.xpath(
                "//ul[@class=\"breadcrumb\"]/li[3]/a/text()"
            ).get(),
            "description": response.xpath(
                "//div[@id=\"product_description\"]/following-sibling::p/text()"
            ).get(),
            "upc": response.xpath(
                "//th[text()=\"UPC\"]/following-sibling::td/text()"
            ).get(),
        }
