from langchain_openai import ChatOpenAI
from src.cmd_selector.selector import ModelSelector

import os

from src.docx2graph.from_llm.creator_pipeline import GraphLLMCreatorPipeline
os.environ["NEO4J_URI"] ="bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "kodin"
os.environ["NEO4J_PASSWORD"] = "12345678"
os.environ["OPENAI_API_KEY"] = "sk-kFANI4tptQfVJAZKpbRxDNBVODFDrOdk"

def main():
    selector_llm = ModelSelector({
        '1': {
            'name': 'gpt-3.5-turbo-0125'
        },
        '2':{
            'name': 'gpt-4-turbo-preview'
        }
    })
    selector_docs = ModelSelector({
        '1': {
            'name': 'assets/dozor (all)',
        },
        '2': {
            'name': 'assets/dozor/install.docx',
        },
        '3': {
            'name': 'assets/dozor/usage_big.docx',
        }
    })
    
    # choice model
    model_name_str = selector_llm.run()
    print(model_name_str)
    model=ChatOpenAI(model_name=model_name_str, base_url='https://api.proxyapi.ru/openai/v1') 
    
    # choice docs
    docs_path = selector_docs.run()
    save_type = input('neo4j?[y/N]')
        
    # create graph
    pipeline = GraphLLMCreatorPipeline(llm=model, documents_path=docs_path)    
    doc_сhunks=pipeline.parse_documents(chunk_size=512, chunk_overlap=24)
    res_graph = pipeline.load_in_graph(doc_сhunks, db_name='gpt35-usage-big', save_type=save_type)
    
    print('Done!')
    
if __name__ == "__main__":
    main()