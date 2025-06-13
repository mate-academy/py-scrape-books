from typing import Any, AsyncIterator, Iterable, Optional, Union
from scrapy import signals
from scrapy.http import Request, Response
from scrapy.crawler import Crawler
from scrapy.spiders import Spider


class BookscraperSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "BookscraperSpiderMiddleware":
        middleware_instance = cls()
        crawler.signals.connect(
            middleware_instance.spider_opened, signal=signals.spider_opened
        )
        return middleware_instance

    def process_spider_input(
        self, response: Response, spider: Spider
    ) -> Optional[None]:
        return None

    def process_spider_output(
        self,
        response: Response,
        result: Iterable[Union[Request, Any]],
        spider: Spider,
    ) -> Iterable[Union[Request, Any]]:
        for item in result:
            yield item

    def process_spider_exception(
        self,
        response: Response,
        exception: Exception,
        spider: Spider,
    ) -> Optional[Iterable[Union[Request, Any]]]:
        return None

    async def process_start(
        self, start: AsyncIterator[Union[Request, Any]]
    ) -> AsyncIterator[Union[Request, Any]]:
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider: Spider) -> None:
        spider.logger.info("Spider opened: %s", spider.name)


class BookscraperDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "BookscraperDownloaderMiddleware":
        middleware_instance = cls()
        crawler.signals.connect(
            middleware_instance.spider_opened, signal=signals.spider_opened
        )
        return middleware_instance

    def process_request(
        self, request: Request, spider: Spider
    ) -> Optional[Union[Request, Response]]:
        return None

    def process_response(
        self,
        request: Request,
        response: Response,
        spider: Spider,
    ) -> Union[Response, Request]:
        return response

    def process_exception(
        self,
        request: Request,
        exception: Exception,
        spider: Spider,
    ) -> Optional[Union[Response, Request]]:
        return None

    def spider_opened(self, spider: Spider) -> None:
        spider.logger.info("Spider opened: %s", spider.name)
