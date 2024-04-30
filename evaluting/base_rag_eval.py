import os
import pandas as pd
from src.cmd_selector.selector import ModelSelector
from langchain_community.document_loaders import Docx2txtLoader

from src.rag_pipelines.base_rag import BaseRAGChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
import datasets
import json

from nltk.translate.bleu_score import sentence_bleu

from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_relevancy,
    answer_similarity
)
from ragas import evaluate
from langchain_community.llms import GigaChat
from langchain_community.embeddings.gigachat import GigaChatEmbeddings


os.environ["OPENAI_API_KEY"] = "sk-kFANI4tptQfVJAZKpbRxDNBVODFDrOdk"
os.environ["OPENAI_BASE_URL"] = 'https://api.proxyapi.ru/openai/v1'

auth_data = "Y2Y0Yjg5OGQtMTBhMi00ZjYwLWIyYTUtY2U5YTY0ODhhYWM5OjUwMTA5YjYzLTMxYjgtNDhiZS1hNTE2LTBkMzkwN2FjNTNjZA=="
os.environ["GIGACHAT_CREDENTIALS"] = auth_data


embedding_model  = GigaChatEmbeddings(scope="GIGACHAT_API_PERS", verify_ssl_certs=False)
llm = GigaChat(model='GigaChat-Plus',verify_ssl_certs=False, scope="GIGACHAT_API_PERS")


def calculate_bleu(row):
    reference = row['answer'].split()  # Токенизация референсного перевода
    candidate = row['ground_truth'].split()  # Токенизация гипотезы
    return sentence_bleu([reference], candidate)
    
    
prompt = ChatPromptTemplate.from_template("""You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
    Question: {question} 
    Context: {context} 
    Answer:""")

import glob
file_names_for_rag_eval = glob.glob('assets/*/*.docx')
print(file_names_for_rag_eval)
def main():
    selector_eval = ModelSelector({
            '1': {
                'name': 'Сделать eval заново.'
            },
            '2':{
                'name': 'По собранному датасету.'
            }},
            title='Что вы хотите сделать?'
            )
    NAME_RAN = input("name: ")
    
    if selector_eval.run() == 'Сделать eval заново.':
        print('Сделать eval заново.')
        rag = BaseRAGChain(
            llm = llm,
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                           chunk_overlap=0),
            embeddings_model = embedding_model,
            prompt = prompt,
            vector_strore=Chroma
        )
        
        
        docs=[]
        for file_name in file_names_for_rag_eval:
            loader = Docx2txtLoader(file_name)
            docs += loader.load()
            
        rag.chanking_data(docs)
        rag.collect_chain()
        
        test_dataset = pd.read_csv('/Applications/programming/kg_llm/notebooks/test_set_29.csv')
        
    else:
        print('По собранному датасету.')
        test_dataset = pd.read_csv(f'{NAME_RAN}.csv')

    test_dataset['answer'] = test_dataset['question'].apply(lambda x: rag(x.strip()))
    test_dataset['contexts'] = test_dataset['contexts'].apply(lambda x:[x])
    
    test_dataset_dict = datasets.Dataset.from_dict(test_dataset)

    result = evaluate(
        test_dataset_dict,
        metrics=[
            faithfulness,
            context_relevancy,
            answer_relevancy,
            answer_similarity,
        ],
        #llm=llm,
        #embeddings=embedding_model
    )
    

    test_dataset['bleu_score'] = test_dataset.apply(calculate_bleu, axis=1)

    result['bleu_score'] = test_dataset['bleu_score'].mean()

    print(result)
    
    # save result in json file
    with open(f'result_{NAME_RAN}.json', 'w') as f:
        json.dump(result, f, indent=4)
    
    test_dataset.to_csv(f'test_{NAME_RAN}.csv', index=False)
        

if __name__ == "__main__":
    main()