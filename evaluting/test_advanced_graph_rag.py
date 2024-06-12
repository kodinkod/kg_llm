import logging

import hydra
import pandas as pd
from dotenv import load_dotenv
from hydra.utils import instantiate
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from omegaconf import DictConfig

from src.rag_pipelines.graph_rag import GraphRAGChain

load_dotenv("examples/rags/.env")

logging.basicConfig(level=logging.WARNING)


@hydra.main(
    version_base=None,
    config_path="../configs/",
    config_name="advanced_graph_rag_test.yaml",
)
def my_app(cfg: DictConfig) -> None:
    prompt = instantiate(cfg.prompt)
    graph = Neo4jGraph(database=cfg.db_name)
    llm = instantiate(cfg.llm2rag)
    embedding_model = instantiate(cfg.embedding2rag)
    vector_index = Neo4jVector.from_existing_graph(
        embedding_model,
        search_type="hybrid",
        node_label="to_indexing",
        text_node_properties=["text", "id"],
        embedding_node_property="embedding",
        database=cfg.db_name,
        index_name="main_index",
    )

    retriever = vector_index.as_retriever(search_kwargs={"k": 10})
    GRAPHRAG = GraphRAGChain(llm=llm, retriever=retriever, graph=graph, prompt=prompt)
    GRAPHRAG.collect_chain()

    test_dataset = pd.read_csv(cfg.test_set_path)
    print("Starting test...")
    test_dataset["answer"] = test_dataset["question"].apply(
        lambda x: GRAPHRAG(x.strip())
    )
    test_dataset["context"] = test_dataset["contexts"].apply(lambda x: [x])

    print(f"Done! Result save to {cfg.name}_test.csv")
    test_dataset.to_csv(f"{cfg.name}_test.csv", index=False)


if __name__ == "__main__":
    my_app()
