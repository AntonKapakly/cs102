from typing import List

import requests
from bs4 import BeautifulSoup
from db import News


def extract_news(parser: BeautifulSoup) -> List[News]:
    """ Extract news from a given web page """
    news_list = []
    table = parser.find("table", {"class": "itemlist"})
    trs = table.find_all(lambda tag: tag.name == "tr" and tag.get("class") != ["spacer"])[:-2]
    for i in range(len(trs) // 2):
        nid = trs[i * 2]["id"]
        title = trs[i * 2].find_all("td", {"class": "title"})[-1].find("a").text
        try:
            author = trs[i * 2 + 1].find("a", {"class": "hnuser"}).text
        except AttributeError:
            author = ""
        url = trs[i * 2].find_all("td", {"class": "title"})[-1].find("a")["href"]
        try:
            comments = int(trs[i * 2 + 1].find_all("a")[-1].text.split()[0])
        except ValueError:
            comments = 0
        try:
            points = int(
                trs[i * 2 + 1]
                .find_all("td", {"class": "subtext"})[-1]
                .find("span", {"class": "score"})
                .text.split()[0]
            )
        except AttributeError:
            points = 0
        label = None
        news_list.append(
            News(
                id=nid,
                title=title,
                author=author,
                url=url,
                comments=comments,
                points=points,
                label=label,
            )
        )
    return news_list


def extract_next_page(parser):
    """ Extract next page URL """
    table = parser.find("table", {"class": "itemlist"})
    trs = table.find_all(lambda tag: tag.name == "tr" and tag.get("class") != ["spacer"])[-1]
    next_page_URL = trs.find("td", {"class": "title"}).find("a")["href"]
    return next_page_URL


def get_news(url, n_pages=1):
    """ Collect news from a given web page """
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(news_list)
        n_pages -= 1
    return news
