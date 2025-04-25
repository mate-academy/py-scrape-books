import scrapy
from books_scraper.items import BooksScraperItem


class BookSpider(scrapy.Spider):
    name = "book"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: scrapy.http.Response) -> None:
        for book in response.css("article.product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            full_url = response.urljoin(book_url)
            yield response.follow(full_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response: scrapy.http.Response) -> None:
        title = response.css("h1::text").get()
        price = response.css("p.price_color::text").get()
        availability = response.css(
            "p.availability::text"
        ).getall()[-1].strip()
        url = response.url

        rating_class = response.css("p.star-rating::attr(class)").get()
        rating = rating_class.replace(
            "star-rating", ""
        ).strip() if rating_class else ""

        category = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get()

        description = response.css(
            "meta[name='description']::attr(content)"
        ).get()
        if description:
            description = description.strip()

        upc = response.css("table tr:nth-child(1) td::text").get()

        # Create an instance of BooksScraperItem and yield it
        item = BooksScraperItem(
            title=title,
            price=price,
            availability=availability,
            url=url,
            rating=rating,
            category=category,
            description=description,
            upc=upc
        )
        yield item
