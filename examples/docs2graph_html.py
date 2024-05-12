import sys
import os
sys.path.insert(0, os.getcwd())


from src.docx2graph.from_docx_structure.utils import build_knowledge_graph, draw_graph, get_triples_from_dcx, get_json_from_graph
from docx_parser.document_parser import DOCXParser

doc_path="/Applications/programming/kg_llm/assets/dozor/dozor.docx"
parser = DOCXParser()
parser.parse(doc_path)

triples, _ = get_triples_from_dcx(parser.get_lines_with_meta())
G = build_knowledge_graph(triples)
link_data_json = get_json_from_graph(G)

draw_graph('test', link_data_json)