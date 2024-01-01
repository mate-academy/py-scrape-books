BOT_NAME = "book_scraper"

SPIDER_MODULES = ["book_scraper.spiders"]
NEWSPIDER_MODULE = "book_scraper.spiders"

ROBOTSTXT_OBEY = True

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
