import scrapy
from scrapy.http import Response


class BookSpider(scrapy.Spider):
    name = "book"
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_detail_url = book.css("h3 a::attr(href)").get()
            yield scrapy.Request(
                url=response.urljoin(book_detail_url), callback=self._parse_single_book
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _convert_str_to_num(response: Response) -> int:
        word_to_number = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        word = (
            response.xpath('//p[contains(@class, "star-rating")]/@class')
            .get()
            .split()[-1]
        )
        return word_to_number[word]

    @staticmethod
    def _parse_single_book(response: Response) -> dict:
        title = response.css("h1::text").get()
        price = response.css(".price_color::text").get()
        amount_in_stock = int(
            response.xpath('//th[text()="Availability"]/following-sibling::td/text()')
            .get()
            .strip()
            .split()[2][1:3]
        )
        rating = BookSpider._convert_str_to_num(response)
        category = response.xpath(
            "//li[@class='active']/preceding-sibling::li/a/text()"
        ).getall()[-1]
        description = response.xpath(
            '//div[@id="product_description" and @class="sub-header"]/following-sibling::p[1]/text()'
        ).get()
        upc = response.xpath('//th[text()="UPC"]/following-sibling::td/text()').get()
        return {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
