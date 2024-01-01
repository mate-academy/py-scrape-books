from typing import Iterable
from scrapy import signals, Spider
from scrapy.http import Response, Request


class BookScraperSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler: Spider) -> "BookScraperSpiderMiddleware":
        instance = cls()
        crawler.signals.connect(
            instance.spider_opened, signal=signals.spider_opened
        )
        return instance

    def process_spider_input(
            self, response: Response, spider: Spider
    ) -> None:
        # Your implementation here
        pass

    def process_spider_output(
        self, response: Response, result: Iterable[Request], spider: Spider
    ) -> Iterable[Request]:
        for item_or_request in result:
            yield item_or_request

    def process_spider_exception(
        self, response: Response, exception: Exception, spider: Spider
    ) -> Iterable[Request]:
        # Your implementation here
        pass

    def process_start_requests(
        self, start_requests: Iterable[Request], spider: Spider
    ) -> Iterable[Request]:
        for request in start_requests:
            yield request

    def spider_opened(self, spider: Spider) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)


class BookScraperDownloaderMiddleware:
    @classmethod
    def from_crawler(
            cls, crawler: Spider
    ) -> "BookScraperDownloaderMiddleware":
        instance = cls()
        crawler.signals.connect(
            instance.spider_opened, signal=signals.spider_opened
        )
        return instance

    def process_request(
        self, request: Request, spider: Spider
    ) -> None:
        # Your implementation here
        pass

    def process_response(
        self, request: Request, response: Response, spider: Spider
    ) -> Response:
        return response

    def process_exception(
        self, request: Request, exception: Exception, spider: Spider
    ) -> Iterable[Request]:
        # Your implementation here
        pass

    def spider_opened(self, spider: Spider) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)
