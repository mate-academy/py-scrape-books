import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response):
        for book in response.css("article.product_pod"):
            title = book.css("h3 a::attr(title)").get()
            price = float(book.css("p.price_color::text").get()[1:])
            rating = book.css("p.star-rating::attr(class)").re_first(
                "star-rating (\w+)"
            )
            book_url = book.css("h3 a::attr(href)").get()

            yield response.follow(
                book_url,
                self.parse_book,
                meta={
                    "title": title,
                    "price": price,
                    "rating": rating,
                },
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_book(self, response):
        title = response.meta["title"]
        price = response.meta["price"]
        amount_in_stock = int(
            response.css("p.instock.availability::text").re_first(r"\d+")
        )
        rating = response.meta["rating"]
        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        description = response.css("#product_description ~ p::text").get()
        upc = (
            response.css("table.table-striped tr:nth-child(1) td::text").get()
        )

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
