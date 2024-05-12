from typing import Any, List

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever


class NeighboursRetriever(BaseRetriever):

    documents: List[Document]
    """List of documents to retrieve from."""
    k: int
    """Number of top results to return"""
    def __init__(self, base_retriver=None, *args, **kwargs):
        super().__init__(*args, **kwargs)  

        if base_retriver is None:
            raise ValueError("base_retriver not None")
        self.base_retriver = base_retriver
        

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        base_retrivers = self.base_retriver.get_relevant_documents(query)
        return base_retrivers
