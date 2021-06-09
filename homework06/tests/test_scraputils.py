import typing as tp

import pytest
import responses
import scraputils
from _pytest.fixtures import SubRequest
from bs4 import BeautifulSoup


@pytest.fixture(params=[1, 2])
def raw(request: "SubRequest") -> tp.Tuple[bytes, int]:
    with open(f"tests/test_data/page{request.param}.txt", "rb") as page:
        raw = page.read()
    return raw, request.param


@pytest.fixture
def parser(raw: tp.Tuple[bytes, int]) -> tp.Tuple[BeautifulSoup, int]:
    return BeautifulSoup(raw[0], "html.parser"), raw[1]


def test_scraputils_extract_next_page_returns_href(parser: tp.Tuple[BeautifulSoup, int]) -> None:
    href = scraputils.extract_next_page(parser[0])
    assert href == f"news?p={parser[1] + 1}"


def test_extract_news_returns_list_news(parser: tp.Tuple[BeautifulSoup, int]) -> None:
    news = scraputils.extract_news(parser[0])
    expected_len = 30
    assert len(news) == expected_len
    assert not any([item.label for item in news])
    assert len(set([item.id for item in news])) == len(news)


@responses.activate
def test_get_news_returns_next_page(raw: tp.Tuple[bytes, int]) -> None:
    responses.add(
        method=responses.GET,
        url="https://news.ycombinator.com/" + (f"/news?p={raw[1]}" if raw[1] != 1 else ""),
        body=raw[0].decode(),
        status=200,
    )
    news = scraputils.get_news(
        "https://news.ycombinator.com/" + (f"/news?p={raw[1]}" if raw[1] != 1 else "")
    )
    assert len(news) == 30
