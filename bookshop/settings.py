BOT_NAME = "bookshop"

SPIDER_MODULES = ["bookshop.spiders"]
NEWSPIDER_MODULE = "bookshop.spiders"


ROBOTSTXT_OBEY = False

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
