import os
import hydra
from omegaconf import DictConfig
from src.graph_chunks.splitter import GrapSplitterTfIdf
from langchain_community.graphs import Neo4jGraph
from langchain_community.document_loaders import Docx2txtLoader
from hydra.utils import instantiate
import tqdm

from src.graph_chunks.splitter_by_structure import SplitterStructure

@hydra.main(version_base=None, config_path="../configs/", config_name="docx2graph_tfidf.yaml")
def my_app(cfg: DictConfig) -> None:
    llm2eval = instantiate(cfg.llm2eval)
    
    os.environ["NEO4J_URI"] =cfg.neo4j.NEO4J_URI
    os.environ["NEO4J_USERNAME"] = cfg.neo4j.NEO4J_USERNAME
    os.environ["NEO4J_PASSWORD"] = cfg.neo4j.NEO4J_PASSWORD
    
    base_splitter = SplitterStructure()
    splitter = GrapSplitterTfIdf(splitter=base_splitter)
    
    # vectorize documents
    # get keywords for documents
    documents=[]
    for doc_path in tqdm.tqdm(cfg.file_names_for_rag_eval):
        # load docs
        loader = Docx2txtLoader(doc_path)
        documents += loader.load()
    
    # find keywords in document in documents lvl
    text_document =[doc.page_content for doc in documents]
    prprocess_text_chunks = [splitter.preprocess_text(text) for text in text_document]
    lemmatized_text_chunks = [splitter.lemmatize(text) for text in prprocess_text_chunks]
    documents_keywords = splitter.vectorize_tfidf(lemmatized_text_chunks)
    
    graph = Neo4jGraph(database='chunk-keyword-structure')
    # clean graph 
    graph.query("MATCH (n) DETACH DELETE n")

    # get keywords for chunks inside documents lvl
    for i, doc_path in enumerate(tqdm.tqdm(cfg.file_names_for_rag_eval)):
        print('process: ', doc_path)
        
        
        # split docs, create graph
        graph_document, _, _ = splitter.split_documents(doc_path, 
                                                  name_docs=doc_path,
                                                  docs_keywords=documents_keywords[i], 
                                                  document_content=text_document[i])
        for node in graph_document.nodes:
            if node.type == 'chunks':
                tl_dr=llm2eval.invoke(f"{node.properties['text']} TL;DR").content
                node.properties['tl_dr']=tl_dr
        
        graph.add_graph_documents(
            [graph_document],
            baseEntityLabel=True,
            include_source=True
        )
        break
    
if __name__ == "__main__":
    my_app()   
    