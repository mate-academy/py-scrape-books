from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Response


class ToscrapeSpider(CrawlSpider):
    name = "toscrape"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    rules = (
        Rule(
            LinkExtractor(
                restrict_xpaths="//article[@class='product_pod']/h3/a"
            ),
            callback="parse_item",
            follow=False,
        ),
        Rule(
            LinkExtractor(restrict_xpaths="//li[@class='next']"), follow=True
        ),
    )

    def parse_item(self, response: Response) -> dict:
        rating = {
            "Zero": 0,
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        item = {}
        item["title"] = response.xpath(
            '//div[contains(@class, "product_main")]/h1/text()'
        ).get()
        item["price"] = float(
            response.xpath(
                '//div[contains(@class, "product_main")]'
                '/p[@class="price_color"]/text()'
            )
            .get()
            .replace("£", "")
            .strip()
        )
        item["amount_in_stock"] = int(
            response.css(".instock.availability::text").re_first(r"\d+")
        )
        item["rating"] = rating[
            response.css(".product_main .star-rating::attr(class)")
            .get()
            .replace("star-rating", "")
            .strip()
        ]
        item["category"] = response.css(
            ".breadcrumb li:nth-child(3) a::text"
        ).get()
        item["description"] = response.xpath(
            '//div[@id="product_description"]/../p/text()'
        ).get()
        item["upc"] = response.xpath(
            "//th[text()='UPC']/following-sibling::td/text()"
        ).get()
        return item
