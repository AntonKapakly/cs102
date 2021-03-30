import typing as tp
from math import log

import pytest
from db import Base, News
from hackernews import (
    add_to_db_if_not_exists,
    create_and_fit_model,
    get_classified_news,
    get_inference_data,
    get_train_data,
    get_unclassified_news,
)
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session, sessionmaker


def db_set_up(engine: "Engine") -> None:
    Base.metadata.create_all(bind=engine)


def db_tear_down(session: "Session") -> None:
    session.query(News).delete()
    session.commit()
    session.close()


@pytest.fixture
def engine() -> "Engine":
    return create_engine("sqlite://")


@pytest.fixture(scope="function")
def session(engine: "Engine") -> tp.Iterable["Session"]:
    session = sessionmaker(engine)()
    db_set_up(engine)
    yield session
    db_tear_down(session)


def test_add_to_db_if_not_exists(session: "Session") -> None:
    current_count = len(session.query(News).all())
    news = [News(**{"id": 0})]

    add_to_db_if_not_exists(news, session)
    assert current_count + 1 == len(session.query(News).all())

    add_to_db_if_not_exists(news, session)
    assert current_count + 1 == len(session.query(News).all())

    news.append(News(**{"id": 1}))

    add_to_db_if_not_exists(news, session)
    assert current_count + 2 == len(session.query(News).all())


def test_get_unclassified_news(session: "Session") -> None:
    data = get_unclassified_news(session)

    news = [
        News(**{"id": 0, "label": None}),
        News(**{"id": 1, "label": "bad"}),
        News(**{"id": 2, "label": "good"}),
    ]
    add_to_db_if_not_exists(news, session)
    data1 = get_unclassified_news(session)

    assert all([item.label == None for item in data1])
    assert len(data1) == len(data) + 1


def test_get_classified_news(session: "Session") -> None:
    data = get_classified_news(session)
    assert all([item.label != None for item in data])

    news = [
        News(**{"id": 0, "label": None}),
        News(**{"id": 1, "label": "bad"}),
        News(**{"id": 2, "label": "good"}),
    ]
    add_to_db_if_not_exists(news, session)
    data1 = get_classified_news(session)

    assert all([item.label != None for item in data1])
    assert len(data1) == len(data) + 2


def test_get_inference_data(session: "Session") -> None:
    news = [
        News(
            **{
                "id": 0,
                "title": "test0",
                "url": "test_url",
                "author": "test_author",
                "comments": 0,
                "points": 0,
                "label": None,
            }
        ),
        News(
            **{
                "id": 1,
                "title": "test1",
                "url": "test_url",
                "author": "test_author",
                "comments": 0,
                "points": 0,
                "label": "bad",
            }
        ),
        News(
            **{
                "id": 2,
                "title": "test2",
                "url": "test_url",
                "author": "test_author",
                "comments": 0,
                "points": 0,
                "label": "good",
            }
        ),
    ]
    add_to_db_if_not_exists(news, session)
    corpus, unclassified = get_inference_data(session)

    assert corpus[0] == "test0 testurl testauthor comments0 points0"
    assert unclassified == get_unclassified_news(session)
    assert len(corpus) == len(unclassified) == 1


def test_get_train_data(session: "Session") -> None:
    news = [
        News(
            **{
                "id": 0,
                "title": "test0",
                "url": "test_url",
                "author": "test_author",
                "comments": 0,
                "points": 0,
                "label": None,
            }
        ),
        News(
            **{
                "id": 1,
                "title": "test1",
                "url": "test_url",
                "author": "test_author",
                "comments": 0,
                "points": 0,
                "label": "bad",
            }
        ),
        News(
            **{
                "id": 2,
                "title": "test2",
                "url": "test_url",
                "author": "test_author",
                "comments": 0,
                "points": 0,
                "label": "good",
            }
        ),
    ]
    add_to_db_if_not_exists(news, session)
    corpus, labels = get_train_data(session)

    assert corpus[0] == "test1 testurl testauthor comments0 points0"
    assert corpus[1] == "test2 testurl testauthor comments0 points0"
    assert labels[0] == "bad"
    assert labels[1] == "good"
    assert len(corpus) == len(labels) == 2


def test_create_and_fit_model(session: "Session") -> None:
    news = [
        News(
            **{
                "id": 0,
                "title": "test0",
                "url": "test_url",
                "author": "test_author",
                "comments": 0,
                "points": 0,
                "label": None,
            }
        ),
        News(
            **{
                "id": 1,
                "title": "test1",
                "url": "test_url",
                "author": "test_author",
                "comments": 0,
                "points": 0,
                "label": "bad",
            }
        ),
        News(
            **{
                "id": 2,
                "title": "test2",
                "url": "test_url",
                "author": "test_author",
                "comments": 0,
                "points": 0,
                "label": "good",
            }
        ),
    ]
    add_to_db_if_not_exists(news, session)
    corpus, labels = get_train_data(session)
    model = create_and_fit_model(corpus, labels, **{"alpha": 1})

    assert model.alpha == 1

    with pytest.raises(TypeError) as exc:
        model = create_and_fit_model(corpus, labels, **{"alpha": 1, "param": "param"})

    assert "__init__() got an unexpected keyword argument 'param'" == str(exc.value)
