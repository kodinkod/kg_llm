import networkx as nx

from src.docx2graph.graph_node import Header_node, List_node, Paragraph_node
from itertools import chain
import json
import networkx as nx
from src.docx2graph.script_for_graph import header_text, tail_text

def build_knowledge_graph(triples):
    """
    Builds a knowledge graph from a list of triples.

    Parameters:
    - triples (list): List of list representing triples, where each tuple consists of a subject, predicate, and object.
    - subject, object : Header_node or Paragraph_node or List_node;

    Returns:
    - G (networkx.DiGraph): Knowledge graph represented as a directed graph.

    The function iterates through each triple, adds nodes and edges to the graph,
    and assigns the predicate as a label to the edges. The resulting graph captures
    relationships between subjects and objects in the knowledge domain.
    
    """
    
    G = nx.DiGraph()
    for subject, predicate, obj in triples:
        G.add_node(subject.id, text=subject.get_text())
        G.add_node(obj.id, text=obj.get_text())
        
        G.add_edge(subject.id, obj.id, label=predicate)
        
    return G


def is_header(t):
    return ('header' in t) or ('heading' in t)


def is_list(t):
    return 'list' in t


def get_triples_from_dcx(lines_with_meta, start_level = 0, roots = []):
    triples = [] 
    start=None
    num = 0
    fective_start = Header_node(lines_with_meta[0]['text'],
                                lines_with_meta[0]['level'],
                                lines_with_meta[0]['uid']) 
    
    # добавляем fective_start
    roots.append(fective_start)
    prev_node = fective_start
    
    # цикл по всем элементам
    while num < len(lines_with_meta):
        f = False
        
        #lines_with_meta key: 'text', 'level', 'uid', 'type', 'annotations'
        item = lines_with_meta[num]
        print('input: ', item['text'])
       
    
        # встречаем первый заголовок
        if (start is None) and is_header(item['type']):
            print('start', item['text'])
            start =  Header_node(item['text'], item['level'], item['uid']) 
            cur_level = item['level']
            
            if fective_start.text != start.text:
                triples.append([fective_start, 'contains_root', start])
                roots.append(start)
        
        # просто текст под заголовком 
        elif (not is_list(item['type'])) and (not is_header(item['type'])):
            paragraph = Paragraph_node(item['text'], item['uid'])
            print('paragraph', item['text'])
            
            if start is not None:
                if paragraph.text != start.text:
                    triples.append([start, 'contains_paragraph', paragraph])
            else:
                if paragraph.text != fective_start.text:
                    triples.append([fective_start, 'contains_paragraph', paragraph])
                
        
        # встретили список
        elif (start is not None ) and (not is_header(item['type'])):
            print('list', item['text'])
            #prev_node # заголовок списка -  предыдущий прарграф
            
            # собираем все элементы списка в одну node
            cur_list_items=[]
            j=num
            while j < len(lines_with_meta):
                if is_list(lines_with_meta[j]['type']):
                    cur_list_items.append(lines_with_meta[j]['text'] + '\n')
                    j+=1
                else:
                    break
            num = j-1
            cur_list_node = List_node("".join(cur_list_items), item['uid'])
           
            triples.append([prev_node, "list_contain" ,cur_list_node ])    
            #print("+++++++++++")
            #print(list_title)
            #print(cur_list_items)
            #print("+++++++++++++++")
            #print()
            
        elif is_header(item['type']): 
            # встретился headr
            print('header', item['text'])
            
            if item['level'] > cur_level:
                new_node_header = Header_node(item['text'], item['level'], item['uid'])
                
                triples.append([start, 'contains', new_node_header])
                print(f'call for {item["text"]}, lvl {item["level"]}')
                a, next_point = get_triples_from_dcx(lines_with_meta[num:], roots)
                triples += a
                num += next_point
                print('end call')
                continue
                
            else:
                # заменили главный заголовок
                print(f'заменили на {item["text"]}, lvl {item["level"]}')
            
                # должны найти старт - заголовок который ниже по уровню 
                # то есть 3й к 2му привязывается
                # 2й к первомоу 
                # 0й  к root
                
                start = Header_node(item['text'], item['level'], item['uid'])
                roots.append(start)
                #print(roots)
                
                for rt in roots[::-1]:
                    if rt.level < item['level']:
                        f = True
                        triples.append([rt, 'contains_root', start])
                        print('add',[rt.text, 'contains_root', start.text])
                        break  
                if not f:
                    triples.append([roots[0], 'contains_root', start])
                    print('add',[rt.text, 'contains_root', item['text']])
        
        print('skip', item['text'])      
        print(10*"==")
        print(10*"==")
        prev_node =  Header_node(item['text'], -1, item['uid'])  # фективный lvl
        num+=1

    return triples, num

 
 
_attrs = dict(id='id', source='source', target='target', key='key')
 
# This is stolen from networkx JSON serialization. It basically just changes what certain keys are.
def node_link_data(G):
    attrs = dict(id='id', source='source', target='target', key='key')
    
    multigraph = G.is_multigraph()
    id_ = attrs['id']
    source = attrs['source']
    target = attrs['target']
    # Allow 'key' to be omitted from attrs if the graph is not a multigraph.
    key = None if not multigraph else attrs['key']
    
    if len(set([source, target, key])) < 3:
        raise nx.NetworkXError('Attribute names are not unique.')
    data = {}
    
    data['directed'] = G.is_directed()
    data['multigraph'] = multigraph
    data['graph'] = G.graph
    data['nodes'] = [dict(chain(G.nodes[n].items(), [(id_, n[:100]), ('label', G.nodes[n]['text'][:100])])) for n in G]
  
    if multigraph:
        data['links'] = [
            dict(chain(d.items(),
                       [('from', u[:100]), ('to', v[:100]), (key, k)]))
            for u, v, k, d in G.edges(keys=True, data=True)]
    else:
        data['links'] = [
            dict(chain(d.items(),
                       [('from', u[:100]), ('to', v[:100])]))
            for u, v, d in G.edges(data=True)]
    return data


def draw_graph(name, node_link_data):
    nodes_str = str(node_link_data['nodes'])
    edges_str = str(node_link_data['links'])

    middle_text = f"var nodes = new vis.DataSet({nodes_str});\n"
    middle_text += f"var edges = new vis.DataSet({edges_str});\n"

    full_text = header_text + middle_text + tail_text

    with open(f"Graph_for_group_{name}.html",
            "w", encoding="utf-8") as f: 
        f.write(full_text)