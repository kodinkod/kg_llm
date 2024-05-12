import os
import hydra
from omegaconf import DictConfig
from hydra.utils import instantiate
from src.docx2graph.from_docx_structure.graph_node import Chunk_node, PP_node
from langchain_community.graphs.graph_document import GraphDocument, Node,Relationship
from src.docx2graph.from_docx_structure.utils import  extract_style, get_style_level, get_triples_from_dcx, get_GraphDocument_from_triples
from langchain_community.graphs import Neo4jGraph
from docx_parser.document_parser import DOCXParser
from langchain_core.documents.base import Document
import tqdm

#tf_idf_splitter_processor = GrapSplitterTfIdf(None)

@hydra.main(version_base=None, config_path="../configs/", config_name="docx2graph_init.yaml")
def my_app(cfg: DictConfig) -> None:
    llm2eval = instantiate(cfg.llm2eval)
    
    os.environ["NEO4J_URI"] =cfg.neo4j.NEO4J_URI
    os.environ["NEO4J_USERNAME"] = cfg.neo4j.NEO4J_USERNAME
    os.environ["NEO4J_PASSWORD"] = cfg.neo4j.NEO4J_PASSWORD
    
    parser = DOCXParser()
    graph = Neo4jGraph(database='rag-kg-pipeline-new')
    graph.query("MATCH (n) DETACH DELETE n")
    
    # Базовая связь:
    dozor = Node(id='dozor', type="ПП", properties={'name':'Дозор'})
    skan = Node(id='скан-архив', type="ПП", properties={'name':'Скан-архив'})
    gendalf = Node(id='other', type="ПП", properties={'name':'Гендальф'})
    nods = [dozor, skan, gendalf]
    relationships=[]
    for doc_path in tqdm.tqdm(cfg.file_names_for_rag_eval):
        targ = Node(text=doc_path, id=doc_path, type="doc")
        nods.append(targ)
        if 'dozor' in doc_path:
            rel = Relationship(source=dozor, target=targ, type='mention')
        if 'скан-архив' in doc_path:
            rel = Relationship(source=skan, target=targ, type='mention')
        if 'other' in doc_path:
            rel = Relationship(source=gendalf, target=targ, type='mention')
        relationships.append(rel)
    
    source = Document(page_content="r")
    doc = GraphDocument(nodes=nods, relationships=relationships, source=source)
    graph.add_graph_documents(
        [doc],
        baseEntityLabel=True)
    
    for doc_path in tqdm.tqdm(cfg.file_names_for_rag_eval):
        print('process: ', doc_path)
        parser.parse(doc_path)
        
        # проставляем добавленные стили 
        for item in parser.get_lines_with_meta():
            item['level'] = get_style_level(
                extract_style(item['annotations'])
            )

        triples, _ = get_triples_from_dcx(parser.get_lines_with_meta())
        
        r_node=Node(id=doc_path, type="doc", text=doc_path)
        graph_document = get_GraphDocument_from_triples(triples, r_node, doc_path) 
        

        graph.add_graph_documents(
            [graph_document],
            baseEntityLabel=True,
            include_source=True
        )
        
        for node in graph_document.nodes:
            if node.type == 'Chunk_node':
                # добавляем историяю к тектсу     
                paths = graph.query(f"MATCH p=(:Root_node)-[*]->(r) WHERE r.id='{node.id}' RETURN p") 
                
                # сформируем путь:
                roots = ""
                for p in paths[0]['p'][:-1]:
                    if isinstance(p, dict):
                        roots=roots+"/"+p['text']
                roots = roots[1: ]# удалим первый симвл
                
                # добавим к тексту путь, откуда был взят этот текст
                new_text = roots + "\n" + node.properties['text']
                
                # добавляем tl_dr
                tl_dr = llm2eval.invoke(f"{new_text} TL;DR").content
                
                graph.query(f"""MATCH (p) WHERE p.id='{node.id}' SET 
                            p.roots='{roots}', 
                            p.tl_dr='{tl_dr}', 
                            p.text='{new_text}'
                            """) 
                
                
    
if __name__ == "__main__":
    my_app()   
    