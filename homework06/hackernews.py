import typing as tp
from math import log

import requests
from bayes import NaiveBayesClassifier, remove_punctuation
from bottle import redirect, request, route, run, template
from bs4 import BeautifulSoup
from db import News, session
from scraputils import extract_next_page, get_news
from sqlalchemy.orm.session import Session

URL = "https://news.ycombinator.com/"


@route("/")
def root():
    redirect("/news")


def add_to_db_if_not_exists(news: tp.List["News"], s: "Session") -> None:
    for entry in news:
        if len(s.query(News).filter(News.id == entry.id).all()) == 0:
            s.add(entry)
    s.commit()


def get_unclassified_news(s: "Session") -> tp.List["News"]:
    return list(s.query(News).filter(News.label == None).all())


def get_classified_news(s: "Session") -> tp.List["News"]:
    return list(s.query(News).filter(News.label != None).all())


def get_inference_data(s: "Session") -> tp.Tuple[tp.List[str], tp.List["News"]]:
    unclassified = get_unclassified_news(s)
    corpus = []
    for item in unclassified:
        sentence = (
            f"{item.title} {item.url} {item.author}"
            f" comments{int(log(item.comments + 1))} points{int(log(item.points + 1))}"
        )
        corpus.append(remove_punctuation(sentence.lower()))
    return corpus, unclassified


def get_train_data(s: "Session") -> tp.Tuple[tp.List[str], tp.List[str]]:
    classified = get_classified_news(s)
    corpus = []
    labels = []
    for item in classified:
        sentence = (
            f"{item.title} {item.url} {item.author}"
            f" comments{int(log(item.comments + 1))} points{int(log(item.points + 1))}"
        )
        corpus.append(remove_punctuation(sentence.lower()))
        labels.append(item.label)
    return corpus, labels


def create_and_fit_model(
    corpus: tp.List[str], labels: tp.List[str], **kwargs: tp.Any
) -> "NaiveBayesClassifier":
    model = NaiveBayesClassifier(**kwargs)
    model.fit(corpus, labels)
    return model


@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template("news_template", rows=rows)


@route("/add_label/")
def add_label():
    s = session()
    entry = s.query(News).filter(News.id == request.query.id).first()
    entry.label = request.query.label
    s.commit()
    redirect("/news")


@route("/update")
def update_news():
    news = get_news(URL)
    s = session()
    add_to_db_if_not_exists(news, s)
    s.commit()
    redirect("/news")


@route("/classify")
def classify_news():
    s = session()
    corpus, labels = get_train_data(s)
    model = create_and_fit_model(corpus, labels, alpha=1)
    new_corpus, unclassified_news = get_inference_data(s)
    new_labels = model.predict(new_corpus)
    rows = [news for news, label in zip(unclassified_news, new_labels) if label == "good"]
    return template("classify_template", rows=rows)


if __name__ == "__main__":
    run(host="localhost", port=8080)
