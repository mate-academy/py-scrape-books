BOT_NAME = "bookscraper"

SPIDER_MODULES = ["books_scrappy.books_scrap.spiders"]
NEWSPIDER_MODULE = "books_scrappy.books_scrap.spiders"

ADDONS = {}


# Obey robots.txt rules
ROBOTSTXT_OBEY = True

FEED_EXPORT_ENCODING = "utf-8"
