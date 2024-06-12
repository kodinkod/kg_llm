import ssl

import spacy as sp
from nltk.corpus import stopwords
from nltk.translate.bleu_score import sentence_bleu
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ssl._create_default_https_context = ssl._create_unverified_context
nlp = sp.load("ru_core_news_lg")
stop_words = set(stopwords.words("russian"))


def calculate_bleu(row):
    reference = row["answer"].split()
    candidate = row["ground_truth"].split()
    return sentence_bleu([reference], candidate)


def calculate_cosine_similarity_TF_IDF(row):
    documents = [row["answer"], row["ground_truth"]]
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(matrix)
    return similarity[0][1]


def calculate_similarity_spacy(row):
    doc1 = nlp(preprocess(nlp(row["answer"])))
    doc2 = nlp(preprocess(nlp(row["ground_truth"])))
    return doc1.similarity(doc2)


def preprocess(text):
    preprocessed_text = [
        token.lemma_.lower()
        for token in text
        if token.lemma_.lower() not in stop_words and token.is_alpha
    ]
    return " ".join(preprocessed_text)
