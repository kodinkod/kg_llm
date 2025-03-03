from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.rag_pipelines.graph_rag import GraphRAGChain

load_dotenv("examples/rags/.env")


# use database create from: docs2graph_neo4j_advanced
DATABASE_NAME = "sandbox"

prompt = ChatPromptTemplate.from_template(
    """Вы являетесь помощником в выполнении заданий по поиску ответов на вопросы. Используйте приведенные ниже фрагменты извлеченного контекста, чтобы ответить на вопрос. Если вы не знаете ответа, просто скажите, что вы не знаете.
           Вопрос: {question}
           Контекст: {context}
           Ответ:"""
)

graph = Neo4jGraph(database=DATABASE_NAME)

llm_gpt = ChatOpenAI(base_url="https://api.proxyapi.ru/openai/v1")
vector_index = Neo4jVector.from_existing_graph(
    OpenAIEmbeddings(base_url="https://api.proxyapi.ru/openai/v1"),
    search_type="hybrid",
    node_label="to_indexing",
    text_node_properties=["text", "id"],
    embedding_node_property="embedding",
    database=DATABASE_NAME,
    index_name="main_index",
)

retriever = vector_index.as_retriever(search_kwargs={"k": 10})

GRAPHRAG = GraphRAGChain(llm=llm_gpt, retriever=retriever, graph=graph, prompt=prompt)
GRAPHRAG.collect_chain()


if __name__ == "__main__":
    print("Question: Что такое дозор?")
    print("Answer: ", GRAPHRAG("Что такое дозор")["answer"])
