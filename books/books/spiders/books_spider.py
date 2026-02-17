import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        books = response.css("article.product_pod")

        for book in books:
            book_url = response.urljoin(
                book.css("h3 a::attr(href)").get()
            )
            yield response.follow(
                book_url,
                callback=self.parse_book
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        table_rows = response.css("table.table.table-striped tr")

        product_info = {
            row.css("th::text").get(): row.css("td::text").get()
            for row in table_rows
        }

        rating_class = response.css(
            "p.star-rating"
        ).attrib.get("class", "")

        rating = rating_class.replace("star-rating", "").strip()

        description = response.css(
            "#product_description ~ p::text"
        ).get()

        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": response.css(
                "p.instock.availability::text"
            ).re_first(r"\d+"),
            "rating": rating,
            "category": response.css(
                "ul.breadcrumb li:nth-child(3) a::text"
            ).get(),
            "description": description,
            "upc": product_info.get("UPC"),
        }
