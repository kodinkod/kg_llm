import hydra
from omegaconf import DictConfig
from hydra.utils import instantiate
import pandas as pd
import datasets

from nltk.translate.bleu_score import sentence_bleu
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_relevancy,
    answer_similarity
)
from langchain_community.document_loaders import Docx2txtLoader
import json
import logging
logging.basicConfig(level=logging.WARNING)


def calculate_bleu(row):
    reference = row['answer'].split() 
    candidate = row['ground_truth'].split() 
    return sentence_bleu([reference], candidate)

@hydra.main(version_base=None, config_path="../configs/", config_name="base_rag.yaml")
def my_app(cfg: DictConfig) -> None:
    # get model
    llm2eval = instantiate(cfg.llm2eval)
    embedding2eval = instantiate(cfg.embedding2eval)
    
    if not cfg.get('from_exist_answer'):
        llm2rag = instantiate(cfg.llm2rag)
        embedding2rag = instantiate(cfg.embedding2rag)
        
        rag_pipeline = instantiate(cfg.rag_pipeline)
        rag_pipeline.llm = llm2rag
        rag_pipeline.embeddings_model = embedding2rag
        rag_pipeline.vector_strore = instantiate(cfg.db)
        rag_pipeline.prompt = instantiate(cfg.prompt)
        rag_pipeline.text_splitter = instantiate(cfg.splitter)
    
        # load docs
        docs=[]
        for file_name in cfg.file_names_for_rag_eval:
            loader = Docx2txtLoader(file_name)
            docs += loader.load()
            
        rag_pipeline.chanking_data(docs)
        rag_pipeline.collect_chain()
            
        test_dataset = pd.read_csv(cfg.test_set_path)
        
        test_dataset['answer'] = test_dataset['question'].apply(lambda x: rag_pipeline(x.strip()))
        test_dataset['contexts'] = test_dataset['contexts'].apply(lambda x:[x])
    else:
        test_dataset = pd.read_csv(cfg.from_exist_answer)    
    
    test_dataset_dict = datasets.Dataset.from_dict(test_dataset)

    result = evaluate(
        test_dataset_dict,
        metrics=[
            faithfulness,
            context_relevancy,
            answer_relevancy,
            answer_similarity,
        ],
        llm=llm2eval,
        embeddings=embedding2eval
    )
    
    test_dataset['bleu_score'] = test_dataset.apply(calculate_bleu, axis=1)
    result['bleu_score'] = test_dataset['bleu_score'].mean()
    
    # TFIDF
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    def calculate_cosine_similarity_TF_IDF(row):
        documents = [row['answer'], row['ground_truth']]
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform(documents)
        similarity = cosine_similarity(matrix)
        return similarity[0][1]


    # Применение функции к DataFrame
    test_dataset['cos-sim-TF-IDF'] = test_dataset.apply(calculate_cosine_similarity_TF_IDF, axis=1)

    result['cos-sim-TF-IDF'] = test_dataset['cos-sim-TF-IDF'].mean()
    
    # sim-spacy
    import ssl
    from nltk.corpus import stopwords
    import spacy as sp

    # Деактивация проверки сертификатов в NLTK 
    ssl._create_default_https_context = ssl._create_unverified_context
    # Загрузка продвинутой модели spaCy
    nlp = sp.load('ru_core_news_lg')
    # Загрузка списка стоп-слов для русского языка
    stop_words = set(stopwords.words("russian"))

    def calculate_similarity_spacy(row):

        doc1 = nlp(preprocess(nlp(row['answer'])))
        doc2 = nlp(preprocess(nlp(row['ground_truth'])))
        return doc1.similarity(doc2)

    def preprocess(text):
        preprocessed_text = [token.lemma_.lower() for token in text if token.lemma_.lower() not in stop_words and token.is_alpha]
        return ' '.join(preprocessed_text)


    # Применение функции к DataFrame
    test_dataset['sim-spacy'] = test_dataset.apply(calculate_similarity_spacy, axis=1)
    
    result['sim-spacy'] = test_dataset['sim-spacy'].mean()
    
    print(result)
    with open(f'result_{cfg.name}.json', 'w') as f:
        json.dump(result, f, indent=4)
    
    test_dataset.to_csv(f'test_{cfg.name}.csv', index=False)
        

if __name__ == "__main__":
    my_app()