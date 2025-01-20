import subprocess


def run_scrapy_spider() -> None:
    subprocess.run(["scrapy", "crawl", "books", "-O", "books.jl"])


if __name__ == "__main__":
    run_scrapy_spider()
