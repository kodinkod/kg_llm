from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class BaseRAGChain:
    def __init__(
        self,
        llm=None,
        text_splitter=None,
        embeddings_model=None,
        vector_strore=None,
        prompt=None,
    ) -> None:
        # prompt =  ChatPromptTemplate
        self.__all_prepare = False

        self.llm = llm
        self.text_splitter = text_splitter
        self.embeddings_model = embeddings_model
        self.prompt = prompt
        self.vector_strore = vector_strore

    def collect_chain(self):
        if not self.__all_prepare:
            raise ValueError("data should be True")
        self.db = self.vector_strore.from_documents(
            documents=self.splits_docs, embedding=self.embeddings_model
        )
        self.retriever = self.db.as_retriever()

        self.rag_chain = (
            {
                "context": self.retriever | self.format_chanks,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def chanking_data(self, docs: list):
        # list docs
        # docs after docs = loader.load()
        self.splits_docs = self.text_splitter.split_documents(docs)
        self.__all_prepare = True

        return self.splits_docs

    def __call__(self, questions) -> Any:
        return self.rag_chain.invoke(questions)

    @staticmethod
    def format_chanks(docs):
        return "\n\n".join(doc.page_content for doc in docs)
