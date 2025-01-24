import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        for book in response.css(".product_pod"):
            rating_class = book.css(
                "p.star-rating::attr(class)"
            ).re_first(r"star-rating (\w+)")

            detail_url = book.css("h3 a::attr(href)").get()

            yield response.follow(
                detail_url,
                callback=self.parse_product_details,
                meta={
                    "title": book.css(".product_pod h3 a::attr(title)").get(),
                    "price": book.css(".price_color::text").get(),
                    "rating": rating_map.get(rating_class, 0),
                }
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_product_details(self, response: Response) -> None:
        title = response.meta["title"]
        price = response.meta["price"]
        rating = response.meta["rating"]

        upc = response.css("th:contains('UPC') + td::text").get()
        availability = response.css(
            "th:contains('Availability') + td::text"
        ).get()
        availability = int(
            availability.split("(")[-1].split(" ")[0]
        ) if availability else 0
        category = response.css(".breadcrumb li:nth-child(3) a::text").get()
        description = response.css("#product_description + p::text").get()
        image_url = response.css("img::attr(src)").get()

        yield {
            "title": title,
            "price": price,
            "rating": rating,
            "upc": upc,
            "availability": availability,
            "category": category,
            "description": description,
            "image_url": image_url,
        }
