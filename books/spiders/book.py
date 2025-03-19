import scrapy
from scrapy.http import Response

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.book_links = {}

    def _get_all_book_links(self, response: Response) -> None:
        for book in response.css(".product_pod"):
            title = book.css("h3 a::attr(title)").get()
            link = book.css("h3 a::attr(href)").get()
            if title and link:
                self.book_links[title] = response.urljoin(link)

    def _parse_books(self):
        for title, link in self.book_links.items():
            yield scrapy.Request(
                url=link,
                callback=self._parse_single_book,
                meta={"title": title}
            )

    def _parse_single_book(self, response: Response):
        rating_text = response.css("p.star-rating::attr(class)").get()
        rating = next(
            (RATING_MAP[word] for word in RATING_MAP if word in rating_text),
            None
        )
        yield {
            "title": response.meta["title"],
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": response.xpath(
                "//table[@class='table table-striped']"
                "//tr[th[text()='Availability']]/td/text()"
            ).re_first(r"\d+"),
            "rating": rating,
            "category": response.css(
                "#default > div > div > ul > li:nth-child(3) > a::text"
            ).get(),
            "description": response.css(
                "#content_inner > article > p::text"
            ).get(),
            "upc": response.xpath(
                "//table[@class='table table-striped']"
                "//tr[th[text()='UPC']]/td/text()"
            ).get()
        }

    def parse(self, response: Response, **kwargs):
        self._get_all_book_links(response)

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        else:
            yield from self._parse_books()
