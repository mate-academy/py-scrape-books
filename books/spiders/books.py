import scrapy

NUMBER_IN_RATING = {
    "Zero": 0,
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class ProductSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/index.html"]

    def parse(self, response) -> None:
        pages = response.css("ul.pager a::attr(href)").getall()
        if pages:
            yield from response.follow_all(pages, self.parse)

        for book in response.css("article.product_pod"):
            yield response.follow(
                book.css("h3 a::attr(href)").get(), self.parse_book
            )

    def parse_book(self, response):
        title = response.css("div.product_main h1::text").get()
        price = float(response.css(
            "p.price_color::text"
        ).get().replace("£", ""))
        amount_in_stock = int(response.css(
            "tr:contains('Availability') td::text"
        ).get().split()[-2].replace("(", ""))

        num_stars = response.css(
            "div.product_main p.star-rating::attr(class)"
        ).get().split()[-1]
        rating = NUMBER_IN_RATING.get(num_stars)
        category = response.css(
            ".breadcrumb > li"
        )[-2].css("a::text").get()
        description = response.css(
            "div#product_description ~ p::text"
        ).get(),
        upc = response.css(
            "th:contains('UPC') + td::text"
        ).get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc
        }
