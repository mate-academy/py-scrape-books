from typing import Iterable, Any, Generator

import scrapy
from scrapy import signals
from scrapy.http import Response
from scrapy.crawler import Crawler


class AppSpiderMiddleware:
    @classmethod
    def from_crawler(
            cls, crawler: Crawler
    ) -> "AppSpiderMiddleware":
        self_ = cls()
        crawler.signals.connect(
            self_.spider_opened,
            signal=signals.spider_opened
        )
        return self_

    def process_spider_input(
            self,
            response: Response,
            spider: scrapy.Spider
    ) -> None:
        return None

    def process_spider_output(
            self,
            response: Response,
            result: Iterable[scrapy.Request | scrapy.Item],
            spider: scrapy.Spider
    ) -> Generator[scrapy.Request | scrapy.Item, Any, None]:
        for i in result:
            yield i

    def process_spider_exception(
        self,
        response: Response,
        exception: Exception,
        spider: scrapy.Spider
    ) -> Iterable[scrapy.Request | scrapy.Item] | None:
        pass

    def process_start_requests(
        self,
        start_requests: Iterable[scrapy.Request],
        spider: scrapy.Spider
    ) -> Generator[scrapy.Request, Any, None]:

        for response in start_requests:
            yield response

    def spider_opened(self, spider: scrapy.Spider) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)


class AppDownloaderMiddleware:

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "AppDownloaderMiddleware":
        self_ = cls()
        crawler.signals.connect(
            self_.spider_opened,
            signal=signals.spider_opened
        )
        return self_

    def process_request(
        self,
        request: scrapy.Request,
        spider: scrapy.Spider
    ) -> scrapy.Request | Response | None:
        return None

    def process_response(
        self,
        request: scrapy.Request,
        response: Response,
        spider: scrapy.Spider
    ) -> scrapy.Request | Response:
        return response

    def process_exception(
        self,
        request: scrapy.Request,
        exception: Exception,
        spider: scrapy.Spider
    ) -> scrapy.Request | Response:
        pass

    def spider_opened(self, spider: scrapy.Spider) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)
