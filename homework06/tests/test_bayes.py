import pytest
from bayes import NaiveBayesClassifier, argmax, remove_punctuation
import csv


@pytest.mark.parametrize("alpha", [0.1, 0.33, 0.5, 1])
def test_bayes_init(alpha):
    model = NaiveBayesClassifier(alpha=alpha)
    assert model.alpha == alpha


def test_bayes_fit_score():
    with open("tests/test_data/SMSSpamCollection") as f:
        data = list(csv.reader(f, delimiter="\t"))
    X, y = [], []
    for target, msg in data:
        X.append(msg)
        y.append(target)
    X_train, y_train, X_test, y_test = X[:3900], y[:3900], X[3900:], y[3900:]
    model = NaiveBayesClassifier()
    model.fit(X_train, y_train)
    assert 0.95 < model.score(X_test, y_test)


def test_bayes_fit_correctness():
    x = [
        "I love this sandwich",
        "This is an amazing place",
        "I feel very good about these beers",
        "This is my best work",
        "What an awesome view",
        "I do not like this restaurant",
        "I am tired of this stuff",
        "I cant deal with this",
        "He is my sworn enemy",
        "My boss is horrible",
    ]
    y = ["Positive"] * 5 + ["Negative"] * 5
    x = [remove_punctuation(s.lower()) for s in x]
    model = NaiveBayesClassifier()
    model.fit(x, y)
    assert 36 == len(model.probs)
    assert 2 == len(model.probs["awesome"])
    assert 0.03278688524590164 == model.probs["awesome"]["Positive"]
    assert 0.016129032258064516 == model.probs["awesome"]["Negative"]
