import os

import hydra
import tqdm
from hydra.utils import instantiate
from omegaconf import DictConfig

from src.docx2graph.from_llm.creator_pipeline import GraphLLMCreatorPipeline

"""
create graph from docx using LLM.
"""


@hydra.main(
    version_base=None,
    config_path="../../configs/",
    config_name="docx2graph_llm_neo4j.yaml",
)
def main(cfg: DictConfig):
    os.environ["NEO4J_URI"] = cfg.neo4j.NEO4J_URI
    os.environ["NEO4J_USERNAME"] = cfg.neo4j.NEO4J_USERNAME
    os.environ["NEO4J_PASSWORD"] = cfg.neo4j.NEO4J_PASSWORD

    model = instantiate(cfg.llm2eval)
    for doc_path in tqdm.tqdm(cfg.file_names_for_rag_eval):
        save_type = input(f"Add {doc_path} to neo4j?[Y/N]:")
        pipeline = GraphLLMCreatorPipeline(llm=model, documents_path=doc_path)
        doc_сhunks = pipeline.parse_documents(chunk_size=512, chunk_overlap=100)
        _ = pipeline.load_in_graph(doc_сhunks, db_name="sandbox", save_type=save_type)

    print("Done!")


if __name__ == "__main__":
    main()
