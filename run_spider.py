from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from book_parse.spiders.book_spider import BookSpiderSpider

# for pycharm debugger

process = CrawlerProcess(get_project_settings())
process.crawl(BookSpiderSpider)
process.start()
