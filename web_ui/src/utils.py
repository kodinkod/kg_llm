from langchain_community.document_loaders import Docx2txtLoader
import glob
def load_docs(name):
    docs=[]
    if name == 'base':
        paths = glob.glob("assets/base/**")
        for p in paths:
            loader = Docx2txtLoader(p)
            docs += loader.load()
            print(p)
    
    return docs