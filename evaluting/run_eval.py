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
from src.metrics.metric_zoo import calculate_cosine_similarity_TF_IDF, calculate_similarity_spacy, calculate_bleu
import logging
import json
import ast
def parse_array(array_str):
    return ast.literal_eval(array_str)


logging.basicConfig(level=logging.WARNING)

@hydra.main(version_base=None, config_path="../configs/", config_name="rag_eval.yaml")
def my_app(cfg: DictConfig) -> None:
    llm2eval = instantiate(cfg.llm2eval)
    embedding2eval = instantiate(cfg.embedding2eval)

    test_dataset = pd.read_csv(cfg.from_exist_answer, converters={'contexts': parse_array})    
    
    # ragas eval
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
    
    # custom eval
    test_dataset['bleu_score'] = test_dataset.apply(calculate_bleu, axis=1)
    test_dataset['sim-spacy'] = test_dataset.apply(calculate_similarity_spacy, axis=1)
    test_dataset['cos-sim-TF-IDF'] = test_dataset.apply(calculate_cosine_similarity_TF_IDF, axis=1)
    result['bleu_score'] = test_dataset['bleu_score'].mean()
    result['sim-spacy'] = test_dataset['sim-spacy'].mean()
    result['cos-sim-TF-IDF'] = test_dataset['cos-sim-TF-IDF'].mean()
    
    # save in json
    with open(f'{cfg.name}.json', 'w') as file:
        json.dump(result, file)

    
if __name__ == "__main__":
    my_app()