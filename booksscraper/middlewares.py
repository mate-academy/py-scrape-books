from __future__ import annotations

from typing import Any, Generator

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


# useful for handling different item types with a single interface
# from itemadapter import is_item, ItemAdapter


class BookscraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler: {signals}) -> BookscraperSpiderMiddleware:
        # This method is used by Scrapy to create your spiders.
        spider = cls()
        crawler.signals.connect(
            spider.spider_opened,
            signal=signals.spider_opened,
        )
        return spider

    def process_spider_input(
            self,
            response: Any,
            spider: Any,
    ) -> None:
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(
            self,
            response: Any,
            result: Any,
            spider: Any,
    ) -> Generator:
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(
            self,
            response: Any,
            exception: Any,
            spider: Any
    ) -> None:
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(
            self,
            start_requests: Any,
            spider: Any
    ) -> Generator:
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for request in start_requests:
            yield request

    def spider_opened(self, spider: Any) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)


class BooksscraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(
            cls, crawler: {signals}
    ) -> BooksscraperDownloaderMiddleware:
        # This method is used by Scrapy to create your spiders.
        scrapy = cls()
        crawler.signals.connect(
            scrapy.spider_opened,
            signal=signals.spider_opened,
        )
        return scrapy

    def process_request(
            self,
            request: Any,
            spider: Any
    ) -> None:
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(
            self,
            request: Any,
            response: Any,
            spider: Any,
    ) -> Any:
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(
            self,
            request: Any,
            exception: Any,
            spider: Any,
    ) -> None:
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider: Any) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)
