import scrapy
from scrapy.http import Response


class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]
    rating_table = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def parse(self, response: Response, **kwargs) -> None:
        for link in response.css(".product_pod > h3 > a::attr(href)").getall():
            yield scrapy.Request(
                url=response.urljoin(link), callback=self.parse_single_page
            )

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_single_page(self, response: Response) -> dict:
        amount_element = response.xpath("//p[@class='instock availability']")
        availability_text = amount_element.xpath("normalize-space(.)").get()
        amount = availability_text[availability_text.index("(") + 1 :].split()[0]

        rating = response.css(".star-rating::attr(class)").get().split()[-1]

        genre = (
            response.xpath('//ul[@class="breadcrumb"]/li[last()-1]')
            .xpath("normalize-space(.)")
            .get()
        )

        upc = response.xpath(
            (
                "//table[@class='table table-striped']"
                "//tr[th[contains(text(), 'UPC')]]/td/text()"
            )
        ).get()

        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(
                response.css(".product_main > .price_color::text").get()[1:]
            ),
            "amount_in_stock": amount,
            "rating": self.rating_table[rating],
            "category": genre,
            "description": response.css(".product_page > p::text").get(),
            "upc": upc,
        }
