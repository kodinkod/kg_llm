import os
import hydra
from omegaconf import DictConfig
from langchain_community.graphs.graph_document import Node
from src.docx2graph.from_docx_structure.utils import  extract_style, get_style_level, get_triples_from_dcx, get_GraphDocument_from_triples
from langchain_community.graphs import Neo4jGraph
from docx_parser.document_parser import DOCXParser
import tqdm

"""
Create Neo4j graph from docx files structure.
"""

@hydra.main(version_base=None, config_path="../../configs/", config_name="docx2graph_neo4j.yaml")
def my_app(cfg: DictConfig) -> None:
    os.environ["NEO4J_URI"] =cfg.neo4j.NEO4J_URI
    os.environ["NEO4J_USERNAME"] = cfg.neo4j.NEO4J_USERNAME
    os.environ["NEO4J_PASSWORD"] = cfg.neo4j.NEO4J_PASSWORD
    
    parser = DOCXParser()
    graph = Neo4jGraph(database='sandbox')
    graph.query("MATCH (n) DETACH DELETE n")
    
    for doc_path in tqdm.tqdm(cfg.file_names_for_rag_eval):
        print('process: ', doc_path)
        parser.parse(doc_path)

        # проставляем добавленные стили 
        for item in parser.get_lines_with_meta():
            item['level'] = get_style_level(
                extract_style(item['annotations'])
            )

        triples, _ = get_triples_from_dcx(parser.get_lines_with_meta())
        
        r_node=Node(id=doc_path, type="doc", text=doc_path)
        graph_document = get_GraphDocument_from_triples(triples, r_node, doc_path) 

        graph.add_graph_documents(
            [graph_document],
            baseEntityLabel=True,
            include_source=True
        )
        

if __name__ == "__main__":
    my_app()