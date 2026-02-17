import scrapy
from scrapy.http import Response, Request
from typing import Generator, Dict, Any, List, Optional


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS": 16,
    }

    def parse(self, response: Response) -> Generator[Any, None, None]:
        yield from self._parse_catalog(response)
        yield from self._paginate(response)

    def _parse_catalog(
        self, response: Response
    ) -> Generator[Request, None, None]:
        for link in self._extract_book_links(response):
            yield response.follow(link, callback=self.parse_book)

    def _extract_book_links(self, response: Response) -> List[str]:
        return response.css("h3 a::attr(href)").getall()

    def _paginate(
        self, response: Response
    ) -> Generator[Request, None, None]:
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(
        self, response: Response
    ) -> Generator[Dict[str, Any], None, None]:
        info = self._extract_table_data(response)

        yield {
            "title": self._extract_title(response),
            "price": self._extract_price(response),
            "amount_in_stock": self._extract_stock(response),
            "rating": self._extract_rating(response),
            "category": self._extract_category(response),
            "description": self._extract_description(response),
            "upc": info.get("UPC"),
        }

    def _extract_table_data(self, response: Response) -> Dict[str, str]:
        rows = response.css("table.table-striped tr")
        return {
            row.css("th::text").get(): row.css("td::text").get()
            for row in rows
        }

    def _extract_title(self, response: Response) -> Optional[str]:
        return response.css("h1::text").get()

    def _extract_price(self, response: Response) -> Optional[float]:
        price = response.css("p.price_color::text").re_first(r"\d+\.\d+")
        return float(price) if price else None

    def _extract_stock(self, response: Response) -> Optional[int]:
        stock = response.css(
            "p.instock.availability::text"
        ).re_first(r"\d+")
        return int(stock) if stock else None

    def _extract_rating(self, response: Response) -> int:
        classes = response.css(
            "p.star-rating::attr(class)"
        ).get(default="")
        rating_text = classes.split()[-1] if classes else ""
        return self.rating_map.get(rating_text, 0)

    def _extract_category(self, response: Response) -> Optional[str]:
        return response.css(
            "ul.breadcrumb li:nth-last-child(2) a::text"
        ).get()

    def _extract_description(self, response: Response) -> Optional[str]:
        return response.css(
            "#product_description + p::text"
        ).get()