import logging

import hydra
import pandas as pd
from hydra.utils import instantiate
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.vectorstores import FAISS
from omegaconf import DictConfig

from src.rag_pipelines.base_rag import BaseRAGChain

logging.basicConfig(level=logging.WARNING)


@hydra.main(
    version_base=None, config_path="../configs/", config_name="base_rag_test.yaml"
)
def my_app(cfg: DictConfig) -> None:
    prompt = instantiate(cfg.prompt)
    llm = instantiate(cfg.llm2rag)
    text_splitter = instantiate(cfg.splitter)
    embedding2rag = instantiate(cfg.embedding2rag)

    BASERAG = BaseRAGChain(
        llm=llm,
        text_splitter=text_splitter,
        embeddings_model=embedding2rag,
        prompt=prompt,
        vector_strore=FAISS,
    )

    documents = []
    for doc_path in cfg.file_names_for_rag_eval:
        doc = Docx2txtLoader(doc_path)
        documents += doc.load()

    BASERAG.chanking_data(documents)
    BASERAG.collect_chain()

    test_dataset = pd.read_csv(cfg.test_set_path)
    print("Starting test...")

    test_dataset["answer"] = test_dataset["question"].apply(
        lambda x: BASERAG(x.strip())
    )
    test_dataset["context"] = test_dataset["contexts"].apply(lambda x: [x])

    print(f"Done! Result save to {cfg.name}_test.csv")
    test_dataset.to_csv(f"{cfg.name}_test.csv", index=False)


if __name__ == "__main__":
    my_app()
