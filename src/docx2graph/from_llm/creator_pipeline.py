from typing import List, Type
from langchain.text_splitter import TokenTextSplitter
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.graphs.graph_document import GraphDocument
from langchain_community.graphs import Neo4jGraph
from langchain_community.document_loaders import Docx2txtLoader
from langchain_core.language_models.llms import BaseLLM
from langchain_core.documents import Document

class GraphLLMCreatorPipeline():
    def __init__(self, documents_path:str, llm: Type[BaseLLM]):
        self.documents_path = documents_path
        self.llm = llm
        self.llm_transformer = LLMGraphTransformer(llm=self.llm)

    def parse_documents(
            self,
            chunk_size: int = 512,
            chunk_overlap: int = 24,
    ) -> List[Document]:
        """Parses the documents in the documents path

        Args:
            chunk_size (int): The size of each chunk. Defaults to 512.
            chunk_overlap (int): The amount of overlap between chunks. Defaults to 24.

        Returns:
            List[Document]: The parsed documents
        """
        loader = Docx2txtLoader(self.documents_path)
        text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        pages = loader.load_and_split()
        documents = text_splitter.split_documents(pages)
        
        return documents

    
    def load_in_graph(self,
                      documents: List[Document],
                      db_name: str = 'docx2graph',
                      save_type: str = 'N',
                  ) -> List[GraphDocument]:
        """Loads the given documents into a neo4j graph database

        Args:
            documents (List[Document]): The documents to load
            db_name (str): The name of the neo4j database
            save_type (str): save in neo4j or no, default is not.

        Returns:
            List[GraphDocument]: The graph documents
        """
        

        graph_documents: List[GraphDocument] = \
        self.llm_transformer.convert_to_graph_documents(documents)

        if save_type=='Y':
            graph: Neo4jGraph = Neo4jGraph(database=db_name)
            graph.add_graph_documents(
                graph_documents,
                baseEntityLabel=True,
                include_source=True,
            )

        return graph_documents

