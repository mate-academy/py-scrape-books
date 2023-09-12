BOT_NAME = "book_scrapping"

SPIDER_MODULES = ["book_scrapping.spiders"]
NEWSPIDER_MODULE = "book_scrapping.spiders"

ROBOTSTXT_OBEY = True

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
