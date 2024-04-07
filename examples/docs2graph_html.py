import sys
import os
sys.path.insert(0, os.getcwd())


from src.docx2graph.utils import build_knowledge_graph, draw_graph, get_triples_from_dcx, node_link_data
from docx_parser.document_parser import DOCXParser

doc_path="/Applications/programming/kg_llm/dozor/usage_big.docx"
parser = DOCXParser()
parser.parse(doc_path)

triples, _ = get_triples_from_dcx(parser.get_lines_with_meta())
G = build_knowledge_graph(triples)
link_data_json = node_link_data(G)

draw_graph('test', link_data_json)