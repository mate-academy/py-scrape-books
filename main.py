from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def main():
    process = CrawlerProcess(settings={
        **get_project_settings(),
        "FEEDS": {
            "books.jl": {
                "format": "jl",
                "encoding": "utf-8",
                "overwrite": True      #  -O, rewrating
            }
        }
    })

    process.crawl("books")
    process.start()


if __name__ == "__main__":
    main()
