from typing import AsyncIterable, AsyncGenerator, Any, Iterable, Generator

from scrapy import signals, Request, Spider
from scrapy.crawler import Crawler
from scrapy.http import Response


class ScrapeBooksSpiderMiddleware:

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "ScrapeBooksSpiderMiddleware":
        spider = cls()
        crawler.signals.connect(
            spider.spider_opened, signal=signals.spider_opened
        )
        return spider

    def process_spider_input(
            self,
            response: Response,
            spider: Spider
    ) -> None:
        return None

    def process_spider_output(
            self,
            response: Response,
            result: Iterable,
            spider: Spider,
    ) -> Generator[Any, Any, None]:
        for i in result:
            yield i

    def process_spider_exception(
            self,
            response: Response,
            exception: Exception,
            spider: Spider
    ) -> None:
        pass

    async def process_start(
            self, start: AsyncIterable
    ) -> AsyncGenerator[Any, Any]:
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider: Spider) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)


class ScrapeBooksDownloaderMiddleware:

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> None:
        spider = cls()
        crawler.signals.connect(
            spider.spider_opened, signal=signals.spider_opened
        )
        return spider

    def process_request(
            self,
            request: Request,
            spider: Spider,
    ) -> None:
        return None

    def process_response(
            self,
            request: Request,
            response: Response,
            spider: Spider,
    ) -> Response:
        return response

    def process_exception(
            self,
            request: Request,
            exception: Exception,
            spider: Spider) -> None:
        pass

    def spider_opened(self, spider: Spider) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)
