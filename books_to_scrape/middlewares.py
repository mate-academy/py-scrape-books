from scrapy import signals


class BooksToScrapeSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    @staticmethod
    def process_spider_input(response, spider):
        return None

    @staticmethod
    def process_spider_output(response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    @staticmethod
    def process_start_requests(start_requests, spider):
        for r in start_requests:
            yield r

    @staticmethod
    def spider_opened(spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class BooksToScrapeDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    @staticmethod
    def process_request(request, spider):
        return None

    @staticmethod
    def process_response(request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    @staticmethod
    def spider_opened(spider):
        spider.logger.info("Spider opened: %s" % spider.name)
