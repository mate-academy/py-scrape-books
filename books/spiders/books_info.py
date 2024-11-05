import scrapy
from scrapy.http import Response


class BooksInfoSpider(scrapy.Spider):
    name = "books_info"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: Response, **kwargs) -> dict:
        for book in response.css(".product_pod"):
            # Extract the link to the detailed book page
            relative_link = book.css(".image_container a::attr(href)").get()
            detailed_book_url = response.urljoin(relative_link)

            # Create a request to the detailed page with
            # a callback to _parse_detailed_book_info
            yield scrapy.Request(
                detailed_book_url,
                callback=self._parse_detailed_book_info
            )

        # Handle pagination for the next page
        next_page = response.css(".pager .next a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def _parse_detailed_book_info(self, response: Response) -> dict:
        # Parse the detailed book info from the response of the book's page
        return {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(response.css(".price_color::text").get()[1:]),
            "amount_in_stock": response.css(".instock.availability::text")
            .re_first(r"\d+"),
            "rating": response.css(".star-rating::attr(class)")
            .re_first(r"\b(One|Two|Three|Four|Five)\b"),
            "category": response.css(".breadcrumb li")[-2].css("a::text")
            .get(),
            "description": response.css("#product_description + p::text")
            .get(),
            "upc": response.css(".table.table-striped td::text").get()
        }
