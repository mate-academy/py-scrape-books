import scrapy


class BookSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        for book in response.css(".product_pod"):
            url = response.urljoin(book.css("a::attr(href)").get())

            yield scrapy.Request(
                url,
                callback=self.parse_book,
                meta={
                    "title": book.css("a::attr(title)").get(),
                    "price": float(book.css(".price_color::text").get().replace("£", ""))
                }
            )
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


    def parse_book(self, response):
        yield {
            "title": response.meta["title"],
            "price": response.meta["price"],
            "amount_in_stock": self.parse_stock(response),
            "rating": self.parse_rating(response),
            "category": self.parse_category(response),
            "description": self.parse_description(response),
            "upc": self.parse_upc(response),
        }

    def parse_stock(self, response) -> int:
        return int(response.css(".instock.availability::text").re_first(r"\d+") or 0)

    def parse_rating(self, response) -> int:
        rating = response.css(".star-rating::attr(class)").re_first(
            r"One|Two|Three|Four|Five"
        )
        return {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}.get(rating)

    def parse_category(self, response) -> str:
        return response.css("ul.breadcrumb a::text").getall()[-1]

    def parse_description(self, response) -> str:
        return response.css("#product_description + p::text").get()

    def parse_upc(self, response) -> str:
        return response.css(".table.table-striped td::text").get()
