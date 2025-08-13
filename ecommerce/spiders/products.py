import scrapy
from scrapy.http import Response
from typing import Any, Generator, Optional
from ecommerce.items import EcommerceItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    custom_settings = {
        "FEEDS": {
            "books.jl": {"format": "jl", "overwrite": True},
        }
    }

    def parse(  # noqa: D401, ARG002
        self, response: Response, **_: Any
    ) -> Generator[Any, None, None]:
        for link in response.css(
                "article.product_pod h3 a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(  # noqa: D401, PLR6201, ARG002
        self, response: Response, **_: Any
    ) -> Generator[EcommerceItem, None, None]:
        self.logger.debug("Parsing book page: %s", response.url)

        def extract_rating() -> Optional[int]:
            rating_class = response.css("p.star-rating::attr(class)").get()
            if not rating_class:
                return None
            rating_map = {
                "One": 1,
                "Two": 2,
                "Three": 3,
                "Four": 4,
                "Five": 5,
            }
            rating_str = rating_class.split()[-1]
            return rating_map.get(rating_str)

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

        def extract_amount_in_stock() -> Optional[int]:
            amount_str = response.css(".availability::text").re_first(r"\d+")
            return int(amount_str) if amount_str else None

        def extract_price() -> Optional[float]:
            price_str = response.css(".price_color::text").get()
            if not price_str:
                return None
            return float(price_str.replace("£", "").strip())

        yield EcommerceItem(
            title=response.css("h1::text").get(),
            price=extract_price(),
            amount_in_stock=extract_amount_in_stock(),
            rating=extract_rating(),
            category=extract_category(),
            description=extract_description(),
            upc=extract_table_value("UPC"),
        )
