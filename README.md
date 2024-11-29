
## Feature
scrape of https://books.toscrape.com/ website.
we parse this information:
- title
- price
- amount_in_stock
- rating
- category
- description
- upc

here I used the `scrapy` framework for parsing.
And implement and only 1 spider to do such a job.

When completed it, we save all books into `books.jl` file.

