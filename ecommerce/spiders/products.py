import scrapy
from scrapy.http import Response
from typing import Any, Generator, Optional, TypedDict


class Book(TypedDict, total=False):
    title: Optional[str]
    price: Optional[str]
    amount_in_stock: Optional[str]
    rating: Optional[str]
    category: Optional[str]
    description: Optional[str]
    upc: Optional[str]


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    custom_settings = {
        "FEEDS": {
            "books.jl": {"format": "jl", "overwrite": True},
        }
    }

    def parse(  # noqa: D401
        self, response: Response, **_: Any
    ) -> Generator[Any, None, None]:
        for link in response.css(
                "article.product_pod h3 a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(  # noqa: D401, PLR6201
        self, response: Response, **_: Any
    ) -> Generator[Book, None, None]:
        self.logger.debug("Parsing book page: %s", response.url)

        def extract_rating() -> Optional[str]:
            rating_class = response.css(
                "p.star-rating::attr(class)").get()
            return rating_class.split()[-1] if rating_class else None

        def extract_description() -> Optional[str]:
            desc = response.css("#product_description ~ p::text").get()
            return desc.strip() if desc else None

        def extract_category() -> Optional[str]:
            return response.css(".breadcrumb li:nth-child(3) a::text").get()

        def extract_table_value(label: str) -> Optional[str]:
            return response.xpath(
                f"//th[normalize-space()='{label}']"
                "/following-sibling::td/text()"
            ).get()

        yield Book(
            title=response.css("h1::text").get(),
            price=response.css(".price_color::text").get(),
            amount_in_stock=response.css(
                ".availability::text").re_first(r"\d+"),
            rating=extract_rating(),
            category=extract_category(),
            description=extract_description(),
            upc=extract_table_value("UPC"),
        )
