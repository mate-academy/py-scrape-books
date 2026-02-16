
BOT_NAME = "scrape_books"

SPIDER_MODULES = ["scrape_books.spiders"]
NEWSPIDER_MODULE = "scrape_books.spiders"

ADDONS = {}

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

FEED_EXPORT_ENCODING = "utf-8"

FEEDS = {
    "books.jl": {
        "format": "jl",
        "encoding": "utf-8",
    }
}

ITEM_PIPELINES = {
    "scrape_books.pipelines.ScrapeBooksPipeline": 300,
}
