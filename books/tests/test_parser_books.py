import os
import json

import pytest
from scrapy.http import HtmlResponse, Request
from books.spiders.book_spider import BookSpiderSpider

@pytest.fixture
def spider():
    return BookSpiderSpider()

def test_parse_book(spider):
    mock_html = """
    <html>
    <body>
        <ul class="breadcrumb">
            <li><a href="index.html">Home</a></li>
            <li><a href="books.html">Books</a></li>
            <li><a href="poetry.html">Poetry</a></li>
        </ul>
        <div class="product_main">
            <h1>A Light in the Attic</h1>
            <p class="price_color">£51.77</p>
            <p class="instock availability">In stock (22 available)</p>
            <p class="star-rating Three"></p>
        </div>
        <div id="product_description"></div>
        <p>It's hard to imagine a world without A Light in the Attic.</p>
        <table class="table table-striped">
            <tr><th>UPC</th><td>a897fe39b1053632</td></tr>
        </table>
    </body>
    </html>
    """

    request = Request(url="https://books.toscrape.com/fake-book")
    response = HtmlResponse(
        url="https://books.toscrape.com/fake-book",
        body=mock_html,
        encoding="utf-8",
        request=request
    )

    item = next(spider.parse_book(response))

    assert item["title"] == "A Light in the Attic"
    assert item["price"] == "£51.77"
    assert item["amount_in_stock"] == "22"
    assert item["rating"] == 3
    assert item["category"] == "Poetry"
    assert item["upc"] == "a897fe39b1053632"


def test_output_file_exists_and_has_correct_amount_of_data():
    file_path = "books.jl"

    assert os.path.exists(file_path), f"File {file_path} was not found!"

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    assert len(lines) == 1575, f"Expected 1575 books, but got {len(lines)}"

    first_book = json.loads(lines[0])
    expected_keys = [
        "title",
        "price",
        "amount_in_stock",
        "rating",
        "category",
        "description",
        "upc"
    ]

    for key in expected_keys:
        assert key in first_book, f"Missing key '{key}' in the scraped item"
        assert first_book[key] is not None, f"Value for '{key}' is None"
