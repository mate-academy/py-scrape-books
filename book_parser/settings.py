BOT_NAME = "book_parser"

SPIDER_MODULES = ["book_parser.spiders"]
NEWSPIDER_MODULE = "book_parser.spiders"

ADDONS = {}


# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
FEED_FORMAT = "jl"
FEED_URI = "books.jl"
