from typing import Iterable

from scrapy import signals, Spider, Request
from scrapy.crawler import Crawler
from scrapy.http import Response


class ScrapeBooksSpiderMiddleware:

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Spider:
        spider = cls()
        crawler.signals.connect(
            spider.spider_opened, signal=signals.spider_opened
        )
        return spider

    def process_spider_output(
            self,
            response: Response,
            result: Iterable,
            spider: Spider
    ) -> None:
        for i in result:
            yield i

    def process_spider_exception(
            self,
            response: Response,
            exception: Exception,
            spider: Spider
    ) -> None:
        spider.logger.error(
            f"Exception encountered: {exception} on {response.url}"
        )
        return None

    def process_start_requests(
            self,
            start_requests: Request,
            spider: Spider
    ) -> None:
        for req in start_requests:
            yield req

    def spider_opened(self, spider: Spider) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)


class ScrapeBooksDownloaderMiddleware:

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Spider:
        spider = cls()
        crawler.signals.connect(
            spider.spider_opened, signal=signals.spider_opened
        )
        return spider

    def process_exception(
            self,
            request: Request,
            exception: Exception,
            spider: Spider
    ) -> None:
        spider.logger.error(f"Download error: {exception} for {request.url}")
        return None

    def spider_opened(self, spider: Spider) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)
