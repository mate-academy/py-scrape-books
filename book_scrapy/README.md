# Scrape books

- Read [the guideline](https://github.com/mate-academy/py-task-guideline/blob/main/README.md) before start


## Task
Here you will scrape https://books.toscrape.com/ website.
For each of 1000 books you need to parse this information:
- title
- price
- amount_in_stock
- rating
- category
- description
- upc

In this task you should use `scrapy` framework for parsing.
And implement only 1 spider to do such job.

When completed it - save all books into `books.jl` file and commit it.
This task doesn't have auto-tests, so test it manually.

Hints:
- use scrapy documentation for searching for all required information;
- use scrapy best practices & learn how to learn new frameworks;
- make your code as clean as possible;
- separate scraping for different steps to make code cleaner.
