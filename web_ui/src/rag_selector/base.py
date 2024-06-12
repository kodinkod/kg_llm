
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from src.rag_pipelines.base_rag import BaseRAGChain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

PROMPT = ChatPromptTemplate.from_template("""You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
Question: {question} 
Context: {context} 
Answer:""")

BASERAG = BaseRAGChain(
    llm = ChatOpenAI(),
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0),
    embeddings_model = OpenAIEmbeddings(),
    prompt = PROMPT,
    vector_strore=FAISS
)