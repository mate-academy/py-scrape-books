# Scrapy settings for books project

BOT_NAME = "books"

SPIDER_MODULES = ["books.spiders"]
NEWSPIDER_MODULE = "books.spiders"

ROBOTSTXT_OBEY = True

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
