BOT_NAME = "scrape_books"

SPIDER_MODULES = ["scrape_books.spiders"]
NEWSPIDER_MODULE = "scrape_books.spiders"

ROBOTSTXT_OBEY = False

SPIDER_MIDDLEWARES = {
    "scrape_books.middlewares.ScrapeBooksSpiderMiddleware": 543,
}

DOWNLOADER_MIDDLEWARES = {
    "scrape_books.middlewares.ScrapeBooksDownloaderMiddleware": 543,
}

ITEM_PIPELINES = {
    "scrape_books.pipelines.ScrapeBooksPipeline": 300,
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
