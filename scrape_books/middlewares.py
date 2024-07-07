from typing import Any

from scrapy import signals
from scrapy.http import Response, Request


class PyScrapeBooksSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler: Any) -> "PyScrapeBooksSpiderMiddleware":
        middleware_instance = cls()
        crawler.signals.connect(
            middleware_instance.spider_opened, signal=signals.spider_opened
        )
        return middleware_instance

    def process_spider_input(self, response: Response, spider: Any) -> None:
        return None

    def process_spider_output(
        self, response: Response, result: Any, spider: Any
    ) -> Any:
        for item in result:
            yield item

    def process_spider_exception(
        self, response: Response, exception: Exception, spider: Any
    ) -> None:
        pass

    def process_start_requests(self, start_requests: Any, spider: Any) -> Any:
        for request in start_requests:
            yield request

    def spider_opened(self, spider: Any) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)


class PyScrapeBooksDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler: Any) -> "PyScrapeBooksDownloaderMiddleware":
        middleware_instance = cls()
        crawler.signals.connect(
            middleware_instance.spider_opened, signal=signals.spider_opened
        )
        return middleware_instance

    def process_request(self, request: Request, spider: Any) -> None:
        return None

    def process_response(
        self, request: Request, response: Response, spider: Any
    ) -> Response:
        return response

    def process_exception(
        self, request: Request, exception: Exception, spider: Any
    ) -> None:
        pass

    def spider_opened(self, spider: Any) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)
