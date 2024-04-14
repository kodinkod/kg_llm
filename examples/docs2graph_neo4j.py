import sys
import os
sys.path.insert(0, os.getcwd())

from src.docx2graph.utils import  get_triples_from_dcx, get_GraphDocument_from_triples
from langchain_community.graphs import Neo4jGraph
from docx_parser.document_parser import DOCXParser

os.environ["NEO4J_URI"] ="bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "kodin"
os.environ["NEO4J_PASSWORD"] = "12345678"

doc_path="assets/dozor/dozor.docx"
parser = DOCXParser()
parser.parse(doc_path)

triples, _ = get_triples_from_dcx(parser.get_lines_with_meta())
graph_document = get_GraphDocument_from_triples(triples, doc_path)

graph = Neo4jGraph(database='testdb')

#graph.query("CREATE OR REPLACE DATABASE testdb")
graph.add_graph_documents(
    [graph_document],
    baseEntityLabel=True,
    include_source=True
)