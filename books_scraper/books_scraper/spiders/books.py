import scrapy

from books_scraper.books_scraper.items import BooksScraperItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        """Parse catalog page and follow links to book detail pages."""

        book_links = response.css("article.product_pod h3 a::attr(href)").getall()

        for link in book_links:
            yield response.follow(
                link,
                callback=self.parse_book_details,
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(self, response):
        """Parse detailed book information page."""

        item = BooksScraperItem()

        item["title"] = response.css("div.product_main h1::text").get()

        price_text = response.css("p.price_color::text").get()
        item["price"] = response.css("p.price_color::text").get()

        availability_text = response.css("p.availability::text").re_first(r"\d+")
        item["amount_in_stock"] = availability_text

        rating_class = response.css("p.star-rating::attr(class)").get()
        item["rating"] = rating_class.split()[-1] if rating_class else None

        item["category"] = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get()

        description = response.css(
            "#product_description ~ p::text"
        ).get()
        item["description"] = description

        item["upc"] = response.xpath(
            "//th[text()='UPC']/following-sibling::td/text()"
        ).get()

        yield item
