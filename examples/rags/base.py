import glob

from dotenv import load_dotenv
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.rag_pipelines.base_rag import BaseRAGChain

load_dotenv("examples/rags/.env")


def load_docs():
    docs = []
    paths = glob.glob("assets/dozor/**")
    for p in paths:
        loader = Docx2txtLoader(p)
        docs += loader.load()
        print(p)

    return docs


PROMPT = ChatPromptTemplate.from_template(
    """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
Question: {question}
Context: {context}
Answer:"""
)

BASERAG = BaseRAGChain(
    llm=ChatOpenAI(),
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0),
    embeddings_model=OpenAIEmbeddings(),
    prompt=PROMPT,
    vector_strore=FAISS,
)

if __name__ == "__main__":
    print("Loading documents:")
    documents = load_docs()
    BASERAG.chanking_data(documents)
    BASERAG.collect_chain()
    print("complete")

    print("Question: Что такое дозор?")
    print("Answer: ", BASERAG("Что такое дозор"))
