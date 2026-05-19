"""Carga el modelo TF-IDF + Logistic Regression entrenado en el notebook y predice
las 24 probabilidades de género a partir del plot de una película.
"""
from __future__ import annotations

import os
import re
from typing import Dict

import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

for _pkg in ("stopwords", "wordnet", "omw-1.4"):
    try:
        nltk.data.find(f"corpora/{_pkg}")
    except LookupError:
        nltk.download(_pkg, quiet=True)

_STOPWORDS = set(stopwords.words("english"))
_LEMMA = WordNetLemmatizer()


def _clean(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    return " ".join(
        _LEMMA.lemmatize(t) for t in text.split() if t not in _STOPWORDS and len(t) > 2
    )


_tfidf = joblib.load(os.path.join(BASE_DIR, "tfidf.pkl"))
_model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))
_genres = joblib.load(os.path.join(BASE_DIR, "genres.pkl"))


def predict_genres(plot: str) -> Dict[str, float]:
    """Retorna un dict {genero: probabilidad} con las 24 clases."""
    cleaned = _clean(plot)
    x = _tfidf.transform([cleaned])
    probs = _model.predict_proba(x)[0]
    return {g: float(p) for g, p in zip(_genres, probs)}


if __name__ == "__main__":
    sample = "A serial killer decides to teach the secrets of his satisfying career to a video store clerk."
    print(predict_genres(sample))
