from pathlib import Path

import scrapy
from scrapy.http import Response


def get_num_from_txt(word):
    word = word.lower()
    nums = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5
    }
    return nums[word]


class BooksShopSpider(scrapy.Spider):
    name = "books-shop"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        # filename = f"books.jl"
        # Path(filename).write_bytes(response.body)
        # self.log(f"Saved file {filename}")
        for block in response.css("article.product_pod"):
            yield {
                "title": block.css("a::attr(title)").get(),
                "price": block.css("p.price_color::text")[0].get().replace("£", ""),
                "rating":
                    get_num_from_txt(block.css("p.star-rating::attr(class)").get().split(" ")[-1])
            }
            additional_info = response.css("a::attr(href)").get()
            print(additional_info)
            if additional_info is not None:
                additional_info = response.urljoin(additional_info)
                yield scrapy.Request(additional_info, callback=self.parse)
