from pathlib import Path
from time import sleep

import scrapy
from scrapy.http import Response


XPATH_URL_BOOK_LINK = "//section/div/ol/li/article/h3/a/@href"
XPATH_URL_NEXT_PAGE = "//div/ul/li/a/@href"
XPATH_URL_SIDE_BAR = "//aside/div/ul/li/ul/li/a/@href"

BASE_URL = "https://books.toscrape.com/"
THROTTLING_TIME = 0.5


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):

        for link in response.xpath(XPATH_URL_BOOK_LINK).getall():
            full_link = BASE_URL + link

            yield {
                "link": full_link
            }

        next_page = response.xpath(XPATH_URL_NEXT_PAGE).getall()[-1]

        if next_page is not None:
            sleep(THROTTLING_TIME)

            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def get_all_info_from_book_page(self, response: Response) -> dict:
        pass
        

# sidebar
# response.xpath("//aside/div/ul/li/ul/li/a/@href").getall()[3]
#  response.xpath("//h3/a/@href").get()
# "https://books.toscrape.com/"

# next page
# >>> page_items = response.xpath("//div/ul/li/a/@href").getall()
# >>> print(page_items)
# page_items[-1]

# book links
# response.xpath("//section/div/ol/li/article/h3/a/@href").getall()





# if __name__ == "__main__":
#     BookSpider.parse()