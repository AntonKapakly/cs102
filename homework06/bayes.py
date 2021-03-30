from collections import defaultdict, Counter
from math import log
import typing as tp
import string


def remove_punctuation(word: str) -> str:
    translator = str.maketrans("", "", string.punctuation)
    return word.translate(translator)


def argmax(values: tp.DefaultDict[str, float]) -> str:
    if len(values) == 0:
        raise ValueError("argmax() arg is an empty sequence")
    return max(values, key=lambda x: values[x])


class NaiveBayesClassifier:
    def __init__(self, alpha=1):
        self.alpha = alpha

    def fit(self, x, y):
        """ Fit Naive Bayes classifier according to X, y. """
        classes = set(y)
        words = dict()
        for sent, label in zip(x, y):
            for word in sent.split():
                if word not in words:
                    words[word] = defaultdict(int)
                words[word][label] += 1
        n_c = defaultdict(int)
        for c in classes:
            for word in words:
                n_c[c] += words[word][c]
        probs = dict()
        for word in words:
            probs[word] = defaultdict(float)
            for c in classes:
                probs[word][c] = (words[word][c] + self.alpha) / (n_c[c] + self.alpha * len(words))

        class_counts = Counter(y)
        self.probs = probs
        self.classes = classes
        self.class_probs = {i: class_counts[i] / len(y) for i in class_counts}

    def predict(self, x):
        """ Perform classification on an array of test vectors X. """
        prediction = []
        for sent in x:
            probs = defaultdict(float)
            for c in self.classes:
                probs[c] += log(self.class_probs[c])
                for word in sent.split():
                    if word in self.probs:
                        probs[c] += log(self.probs[word][c])
            prediction.append(argmax(probs))
        return prediction

    def score(self, x_test, y_test):
        """ Returns the mean accuracy on the given test data and labels. """
        predicted = self.predict(x_test)
        score = 0
        for i in range(len(y_test)):
            if y_test[i] == predicted[i]:
                score += 1
        return score / len(y_test)
