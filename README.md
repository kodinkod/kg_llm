# Knowledge Graphs in the RAG. GraphGAR.

Integration of the knowledge graph and LLM. The knowledge graph serves as an improved replacement for unstructured data chunk stores in QA systems.

The repository implements:
 - 🛠️ Creating a knowledge graph from the document (docx) structure or using LLM.
 - 💡 A proposal for the integration of the knowledge graph in RAG Pipeline.
 - 🚋 GraphRAG pipeline.
 - 🚀 A web service for working with the QA system based on the knowledge graph.


## install

1. clone repo:
` git clone  https://github.com/kodinkod/kg_llm.git `

2. install dependencies:
```
pip install poetry
poetry install 
poetry shell
```


## Usage
1. We use hydra framework for logging and use cofig.
2. For use all code we need have connection with neo4j db.

> warning: for use neo4j setup configs/neo4j/base.yaml (in config and .env files).
> warning: for use openai LLM add all API keys. (in config and .env files).

### Create graph using structure 

Create html page with graph from docx document.
```
python examples/graph_creation/docs2graph_html.py 
```
[text](output/html_graph_pages/Graph_for_group_test.html)

Load in neo4j (default: 'sandbox' database) graph from docx document.
```
python examples/graph_creation/graph_splitter_neo4j_base.py
```


![example](example.gif)