from py2neo import Graph
from flask import Flask, redirect, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from config import Config
from src.rag_selector.base import BASERAG
from src.rag_selector.graph import GRAPHRAG
from src.rag_pipelines.graph_rag import parse_to_dict
from src.utils import load_docs

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
graph = Graph("bolt://localhost:7687", auth=("kodin", "12345678"), name="method-3")
IDS_GRAPH = []

BASECONTENT= {'questions':'gpt-3.5-turbo',
            'answer_content':'Ответ на вопрос!', 
            'context': ["вариант",'вариант 2'], 
            'len_context':2,
            'distance':[99,100],
            'model_name':'gpt-3.5-turbo',
            'info_pipeline': "",
            'is_graph': False
            }

@app.route('/')
@app.route('/index')
def index():
    return render_template("bot.html", **BASECONTENT)


@app.route("/chat/", methods=["POST"])
def move_forward():
    questions =  request.form.get('question')
    rag_result =  RAG(questions)
    answer = rag_result['answer']
    context = rag_result['context']
    
    BASECONTENT['answer_content'] = answer
    BASECONTENT['questions'] = questions
    meta_extract=[parse_to_dict(doc.page_content)[0] for doc in context]
    BASECONTENT['context'] = [doc['text'] for doc in meta_extract]
    
    if RAG == GRAPHRAG:
        global IDS_GRAPH
        IDS_GRAPH = [doc['id'] for doc in meta_extract]

    return render_template("bot.html", **BASECONTENT)

@app.route("/setup/", methods=["POST"])
def setup():
    doc = request.form.get('dataSelect')
    model = request.form.get('languageModelSelect')
    pipeline = request.form.get('methodSelect')
    
    BASECONTENT['info_pipeline']=f"""   \n 
    документ: {doc},
    модель: {model},\n
    способ: {pipeline}
    """
    global RAG
    if pipeline == 'base':
        RAG = BASERAG
        documents = load_docs(doc)
        RAG.chanking_data(documents)
    if pipeline == 'graph_rag':
        RAG = GRAPHRAG
        BASECONTENT['is_graph'] = True
    
    RAG.collect_chain()
    
    return render_template("bot.html", **BASECONTENT)

@app.route('/graph-data')
def graph_data():
    if len(IDS_GRAPH) == 0:
        return jsonify([])
    new_ids=IDS_GRAPH
    k=0
    for ID in IDS_GRAPH:
        list_contains = graph.run(f"""
                                    MATCH p=(startNode)-[]->(list_node:List_node) WHERE startNode.id='{ID}' RETURN list_node
                                    """)
        for list_node in list_contains:
            new_ids.append(list_node['list_node']['id'])
                
        # тепрь найдем соседей на 3 близкие чанки к текущему
        neighbord = graph.run(f"""
                                MATCH path = (current)-[r*1..3]-(neighbor:Paragraph_node)
                                WHERE current.id = '{ID}'
                                AND NONE(rel IN relationships(path) WHERE type(rel) IN ['MENTION', 'MENTIONS', 'PP_CONTAINS'])
                                WITH neighbor, length(path) AS distance
                                ORDER BY distance
                                RETURN neighbor                                    
                                """)
        
        if k <4:
            for ne in neighbord:
                k+=1
                print(k)
                print(ne['neighbor']['id'])
                new_ids.append(ne['neighbor']['id'])
            
    # Вызовите функцию, получающую данные из Neo4j
    results = graph.run(f"""
                        MATCH path= (d:Root_node)-[r*]->(ent) 
                        WHERE ent.id IN {new_ids}
                        RETURN d, ent, path""")
    data = fetch_graph_data(results)
    return jsonify(data)
    
def fetch_graph_data(results):
    # Здесь возвращаются данные из базы данных Neo4j, преобразованные к нужному формату
    # Это может быть список узлов и список связей
    nodes = []
    edges = []
    exist_rel=[]
    ids_nodes = []
    exist_text = []
    for record in results:
        for node in record['path'].nodes:
            text = get_node_text(node)
            if (node.identity not in ids_nodes) and (text not in exist_text):
                
                ids_nodes.append(node.identity)
                #exist_text.append(text)
                if 'Root_node' in node.labels:
                    nodes.append({"id": node.identity,
                                  "label": text,
                                  "color": {"background": 'red', "border": 'darkred'}})
                else:
                    nodes.append({"id": node.identity,
                                  "label": text})
        
        for rel in record['path'].relationships:            
            exist_rel.append(rel.identity)
            start_node_id = rel.start_node.identity
            end_node_id = rel.end_node.identity
            edges.append({"from": start_node_id, "to": end_node_id})
            
    return {"nodes": nodes, "edges": edges, 'meta': IDS_GRAPH}



def get_node_text(node):
    if node['text']:
        if '<root->' in node['text']:
            return node['text'].split('<root->')[1]
        return node['text']
    else:
        return node['id']
