import scrapy
from booksscraper.items import BookItem


RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: any) -> any:
        """Crawl catalogue pages and follow each book link."""
        get_all = response.css("article.product_pod h3 a::attr(href)").getall()
        for book_url in get_all:
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: any) -> any:
        """Extract all required fields from an individual book page."""
        item = BookItem()
        item["title"] = self._parse_title(response)
        item["price"] = self._parse_price(response)
        item["amount_in_stock"] = self._parse_stock(response)
        item["rating"] = self._parse_rating(response)
        item["category"] = self._parse_category(response)
        item["description"] = self._parse_description(response)
        item["upc"] = self._parse_upc(response)
        yield item

    # ------------------------------------------------------------------ #
    # Private helpers — one per field for clarity                         #
    # ------------------------------------------------------------------ #

    def _parse_title(self, response: any) -> str:
        return response.css("div.product_main h1::text").get()

    def _parse_price(self, response: any) -> float:
        raw = response.css("p.price_color::text").get(default="")
        # Strip currency symbol and convert to float
        return float(raw.replace("Â", "").replace("£", "").strip())

    def _parse_stock(self, response: any) -> int:
        raw = response.css("p.availability::text").getall()
        # The availability text contains the number in parentheses,
        # e.g. "In stock (22 available)"
        for text in raw:
            text = text.strip()
            if text.isdigit():
                return int(text)
            import re
            match = re.search(r"\d+", text)
            if match:
                return int(match.group())
        return 0

    def _parse_rating(self, response: any) -> int:
        word = response.css("p.star-rating::attr(class)").get(default="")
        # class is like "star-rating Three"
        rating_word = word.split()[-1] if word else "One"
        return RATING_MAP.get(rating_word, 0)

    def _parse_category(self, response: any) -> str:
        # Breadcrumb: Home > Category > Book title
        crumbs = response.css("ul.breadcrumb li a::text").getall()
        return crumbs[-1].strip() if len(crumbs) >= 2 else None

    def _parse_description(self, response: any) -> str:
        # Description sits after the #product_description anchor
        return response.css(
            "#product_description ~ p::text"
        ).get(default="").strip()

    def _parse_upc(self, response: any) -> str:
        # First <td> in the product information table
        return response.css(
            "table.table-striped tr:first-child td::text"
        ).get()
