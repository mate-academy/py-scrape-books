from typing import Iterable, Any, Union

import scrapy
from scrapy import signals
from scrapy.http import HtmlResponse, Response


class EcommerceSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler: scrapy.crawler.Crawler) -> Any:
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(
        self, response: HtmlResponse, spider: scrapy.Spider
    ) -> None:
        return None

    def process_spider_output(
        self, response: HtmlResponse, result: Iterable[Any],
        spider: scrapy.Spider
    ) -> Iterable[Any]:
        for i in result:
            yield i

    def process_spider_exception(
        self, response: HtmlResponse, exception: Exception,
        spider: scrapy.Spider
    ) -> None:
        pass

    def process_start_requests(
        self, start_requests: Iterable[scrapy.Request], spider: scrapy.Spider
    ) -> Iterable[scrapy.Request]:
        for r in start_requests:
            yield r

    def spider_opened(self, spider: scrapy.Spider) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)


class EcommerceDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler: scrapy.crawler.Crawler) -> Any:
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(
        self, request: scrapy.Request, spider: scrapy.Spider
    ) -> Union[None, Response, scrapy.Request]:
        return None

    def process_response(
        self, request: scrapy.Request, response: Response,
        spider: scrapy.Spider
    ) -> Union[Response, scrapy.Request]:
        return response

    def process_exception(
        self, request: scrapy.Request, exception: Exception,
        spider: scrapy.Spider
    ) -> Union[None, Response, scrapy.Request]:
        return None

    def spider_opened(self, spider: scrapy.Spider) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)