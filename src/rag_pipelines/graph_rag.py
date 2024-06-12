from typing import Any
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
import re

def most_frequent_string(string_list):
    # Создаем словарь для хранения частоты каждой строки
    frequency_dict = {}
    
    # Считаем частоты строк в массиве
    for s in string_list:
        if s in frequency_dict:
            frequency_dict[s] += 1
        else:
            frequency_dict[s] = 1
            
    # Находим строку с максимальной частотой
    most_frequent = max(frequency_dict, key=frequency_dict.get)
    
    return most_frequent

def parse_to_dict(input_str):
    # Создаем пустой словарь для хранения результатов
    if not '\ntext:' in input_str:
        return {"text": input_str, 'id': input_str}, False
    result_dict = {}
    is_header=False
    
    # Используем регулярные выражения для поиска всех пар ключ-значение
    if not ('\ntl_dr: \ntext:' in input_str):
        pattern = r'\n(tl_dr|text|id):\s*([^\n]+)'
    else:
        is_header=True
        pattern = r'\n(text|id):\s*([^\n]+)'
    entries = re.findall(pattern, input_str)

    # Заполняем словарь найденными парами ключ-значение
    for key, value in entries:
        result_dict[key.strip()] = value.strip()
    
    return result_dict, is_header


class GraphRAGChain():
    def __init__(self, 
                 llm=None,
                 retriever=None,
                 graph = None,
                 prompt=None,
                 ) -> None:
        
        self.llm = llm
        self.retriever = retriever
        self.prompt = prompt
        self.graph = graph  
        
    def collect_chain(self):
        format_docs=lambda x : self.format_chanks(x)
        get_relevant_docs=lambda x: self.get_relevant_docs(x)
        rag_chain_from_docs = (
                RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
        self.rag_chain = RunnableParallel(
            {"context": self.retriever | get_relevant_docs, "question": RunnablePassthrough()}
        ).assign(answer=rag_chain_from_docs)
    
    def __call__(self, questions) -> Any:
        return self.rag_chain.invoke(questions)
    
    def get_relevant_docs(self, docs):
        names_pp = []
        for doc in docs:
            meta, is_header = parse_to_dict(doc.page_content)
        
            root = meta['text'].split('<root->')[0]
            
            pp_product_name = root.split('/')[0]
            names_pp.append(pp_product_name)
            
        most_frequent_pp = most_frequent_string(names_pp)      
        relevant_pp_docs =  [doc for doc in docs if most_frequent_pp in doc.page_content]

        return relevant_pp_docs[:4]
    
    def format_chanks(self, docs):
        exist_root = []
        context = []
        for doc in docs:
            meta, is_header = parse_to_dict(doc.page_content)
    
            root = meta['text'].split('<root->')[0]
            text =  meta['text'].split('<root->')[-1]
            meta_id = meta["id"]

            if not (root in exist_root):
                text = "информация из раздела: Програмный продукт " + root + "\n" + text
                
                if not is_header:
                    context.append(text)
                    exist_root.append(root)
                
                # Содержит текущий узел  лист, если содержит - показываем
                list_contains = self.graph.query(f"""
                                            MATCH p=(startNode)-[]->(list_node:List_node) WHERE startNode.id='{meta_id}' RETURN list_node
                                            """)
                for list_node in list_contains:
                    l_t = list_node['list_node']['text'].split('<root->')[-1]
                    l_r = list_node['list_node']['text'].split('<root->')[0]
                    text = "информация из списка: Програмный продукт " + l_r + "\n" + l_t
                    context.append(text)
                    
                # тепрь найдем соседей на 3 близкие чанки к текущему
                neighbord = self.graph.query(f"""
                                        MATCH path = (current)-[r*1..8]-(neighbor:Chunk_node)
                                        WHERE current.id = '{meta_id}'
                                        AND NONE(rel IN relationships(path) WHERE type(rel) IN ['MENTION', 'MENTIONS', 'PP_CONTAINS'])
                                        WITH neighbor, length(path) AS distance
                                        ORDER BY distance
                                        RETURN neighbor                                    
                                        """)
                            
                for ne in neighbord[:4]:
                    c_t = ne['neighbor']['text'].split('<root->')[-1] # берем текст 
                    c_r = ne['neighbor']['text'].split('<root->')[0]  # берем путь
                    
                    if (not c_r in exist_root):  
                        exist_root.append(c_r)
                        text = "информация из раздела: Програмный продукт " + c_r + "\n" + c_t
                        context.append(text)
                        
        data_split = "\n\n".join(context[:5]).split(" ")
        return " ".join(data_split)







