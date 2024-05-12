
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from langchain_core.documents.base import Document
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import spacy   
import hashlib
import secrets
import re

# Загрузка стоп-слов и пунктуации
nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('russian'))
punctuation = set(string.punctuation)

class GrapSplitterTfIdf(object):
    def __init__(self, splitter):
        self.splitter = splitter
        
        self.nlp_model = spacy.load("ru_core_news_lg")
        self.ngram_range = (1, 6)
        # Определение порога для отбора ключевых слов
        self.threshold = 0.15
        
    def preprocess_text(self, text):
        words = word_tokenize(text.lower())  
        filtered_words = [word for word in words if word not in stop_words and word not in punctuation]
        clean_digits = [re.sub(r'\d', '', s) for s in filtered_words]
        return " ".join(clean_digits)
            
    def lemmatize(self, text):
        doc = self.nlp_model(text.lower())  
        lemmatized_words = [token.lemma_ for token in doc if token.text not in punctuation and token.text not in stop_words]
        return " ".join(lemmatized_words)
    
    def split_documents(self, documents, name_docs="document", docs_keywords=[], document_content=""):
     
        init_splits = self.splitter.split_documents(documents)
        text_chunks =[doc.page_content for doc in init_splits]
        prprocess_text_chunks = [self.preprocess_text(text) for text in text_chunks]
        lemmatized_text_chunks = [self.lemmatize(text) for text in prprocess_text_chunks]
        
        keywords = self.vectorize_tfidf(lemmatized_text_chunks)
        
        nodes = []
        relationships=[]
        for text, keyw in zip(text_chunks, keywords):
            src = Node(id= self.get_random_hash(), 
                       type='chunk', 
                       properties={'text':  text})
            nodes.append(src)
            
            for k in keyw:
                target = Node(id=k, 
                              type='keyword', 
                              properties={'text': k})
                nodes.append(target)
                relationships.append(
                    Relationship(source=src, 
                                target=target, 
                                type='contain_keyword'))
        
        source_document = Document(page_content=document_content, metadata={"name": name_docs})
        
        # добавляем кейворды к самому документу
        for k in docs_keywords:
            # они потом прикрепятся к source_document
            nodes.append(Node(id=k+"_document_key", 
                            type='keyword_document', 
                            properties={'text': k}))
        
        graph_doc = GraphDocument(nodes=nodes, relationships=relationships, source=source_document)
        
        return graph_doc, keywords, text_chunks
    
    
    def vectorize_tfidf(self, documents):
        # Создание объекта TfidfVectorizer
        tfidf_vectorizer = TfidfVectorizer(ngram_range=self.ngram_range)

        # Применение TF-IDF к текстовым данным
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
        
        keywords=[]
        for row in tfidf_matrix:
            # Сопоставляем слова с их TF-IDF весами
            word_scores = {word: score for word, score in zip(tfidf_vectorizer.get_feature_names_out(), row.toarray().flatten())}
            
            # Сортировка слов в документе по весам
            sorted_words = sorted(word_scores.items(), key=lambda item: item[1], reverse=True)
            
            # Берем, например, топ-5 слова с наивысшим весом TF-IDF в качестве ключевых слов
            document_keywords = [word for word, score in sorted_words[:2]]
            
            # Добавляем список ключевых слов для данного документа
            keywords.append(document_keywords)
        
        return keywords
    
    @staticmethod
    def get_random_hash():
        random_bytes = secrets.token_bytes(64)
        hash_object = hashlib.sha256(random_bytes)
        return hash_object.hexdigest()