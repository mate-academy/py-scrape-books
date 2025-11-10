from scrapy.crawler import CrawlerProcess

from book.spiders.books_spiders import BookSpider

process = CrawlerProcess(
    settings={
        "FEEDS": {
            "books.jl": {"format": "jl"},
        },
    }
)

process.crawl(BookSpider)
process.start()
