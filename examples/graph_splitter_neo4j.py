import os
import hydra
from omegaconf import DictConfig
from src.graph_chunks.splitter import GrapSplitterTfIdf
from langchain_community.graphs import Neo4jGraph
from langchain_community.document_loaders import Docx2txtLoader
import tqdm

@hydra.main(version_base=None, config_path="../configs/", config_name="docx2graph_tfidf.yaml")
def my_app(cfg: DictConfig) -> None:
    
    os.environ["NEO4J_URI"] =cfg.neo4j.NEO4J_URI
    os.environ["NEO4J_USERNAME"] = cfg.neo4j.NEO4J_USERNAME
    os.environ["NEO4J_PASSWORD"] = cfg.neo4j.NEO4J_PASSWORD
    
    splitter = GrapSplitterTfIdf(chunk_size=800, chunk_overlap=200)
    
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
    
    graph = Neo4jGraph(database='chunk-keyword-exp5')
    # clean graph 
    graph.query("MATCH (n) DETACH DELETE n")

    # get keywords for chunks inside documents lvl
    for i, doc_path in enumerate(tqdm.tqdm(cfg.file_names_for_rag_eval)):
        print('process: ', doc_path)
        
        # load docs
        loader = Docx2txtLoader(doc_path)
        doc = loader.load()
        
        # split docs, create graph
        graph_document, _, _ = splitter.split_documents(doc, 
                                                  name_docs=doc_path,
                                                  docs_keywords=documents_keywords[i], 
                                                  document_content=text_document[i])
        
        graph.add_graph_documents(
            [graph_document],
            baseEntityLabel=True,
            include_source=True
        )
    
if __name__ == "__main__":
    my_app()   
    