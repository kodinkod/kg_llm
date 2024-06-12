import hydra
from omegaconf import DictConfig
from hydra.utils import instantiate
import pandas as pd
import datasets
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    answer_similarity
)
from langchain_community.document_loaders import Docx2txtLoader
from src.metrics.metric_zoo import calculate_cosine_similarity_TF_IDF, calculate_similarity_spacy, calculate_bleu
import logging
import json
import ast
def parse_array(array_str):
    return ast.literal_eval(array_str)


logging.basicConfig(level=logging.WARNING)

@hydra.main(version_base=None, config_path="../configs/", config_name="base_rag_eval.yaml")
def my_app(cfg: DictConfig) -> None:
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
    
        docs=[]
        for file_name in cfg.file_names_for_rag_eval:
            loader = Docx2txtLoader(file_name)
            docs += loader.load()
            
        rag_pipeline.chanking_data(docs)
        rag_pipeline.collect_chain()
            
        test_dataset = pd.read_csv(cfg.test_set_path)
        
        test_dataset['answer'] = test_dataset['question'].apply(lambda x: rag_pipeline(x.strip()))
        test_dataset['context'] = test_dataset['contexts'].apply(lambda x:[x])
    else:
        test_dataset = pd.read_csv(cfg.from_exist_answer, converters={'contexts': parse_array})    
   
    print(type(test_dataset.loc[0, 'contexts']))
    
    test_dataset_dict = datasets.Dataset.from_dict(test_dataset)

    result = evaluate(
        test_dataset_dict,
        metrics=[
            answer_relevancy,
            answer_similarity,
        ],
        llm=llm2eval,
        embeddings=embedding2eval
    )
    
    test_dataset['bleu_score'] = test_dataset.apply(calculate_bleu, axis=1)
    test_dataset['sim-spacy'] = test_dataset.apply(calculate_similarity_spacy, axis=1)
    test_dataset['cos-sim-TF-IDF'] = test_dataset.apply(calculate_cosine_similarity_TF_IDF, axis=1)
    result['bleu_score'] = test_dataset['bleu_score'].mean()
    result['sim-spacy'] = test_dataset['sim-spacy'].mean()
    result['cos-sim-TF-IDF'] = test_dataset['cos-sim-TF-IDF'].mean()
    
    with open(f'{cfg.name}.json', 'w') as file:
        json.dump(result, file)

    
if __name__ == "__main__":
    my_app()