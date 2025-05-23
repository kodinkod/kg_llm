from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from src.rag_pipelines.graph_rag import GraphRAGChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv
import os

load_dotenv('.env')
prompt = ChatPromptTemplate.from_template("""Вы являетесь помощником в выполнении заданий по поиску ответов на вопросы. Используйте приведенные ниже фрагменты извлеченного контекста, чтобы ответить на вопрос. Если вы не знаете ответа, просто скажите, что вы не знаете. 
           Вопрос: {question} 
           Контекст: {context} 
           Ответ:""")
graph = Neo4jGraph(database='method-3')
llm_gpt = ChatOpenAI(base_url='https://api.proxyapi.ru/openai/v1')
vector_index = Neo4jVector.from_existing_graph(
    OpenAIEmbeddings(base_url='https://api.proxyapi.ru/openai/v1'),
    search_type="hybrid",
    node_label="to_indexing",
    text_node_properties=["tl_dr", "text", "id"],
    embedding_node_property="embedding",
    database='method-3',
    index_name='main_index'
)

retriever = vector_index.as_retriever(search_kwargs={'k': 10})
GRAPHRAG = GraphRAGChain(llm=llm_gpt, retriever=retriever, graph=graph, prompt=prompt)