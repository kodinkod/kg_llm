from langchain_core.documents.base import Document
from docx_parser.document_parser import DOCXParser
from src.docx2graph.from_docx_structure.graph_node import Header_node, Paragraph_node
from src.docx2graph.from_docx_structure.utils import get_triples_from_dcx
from langchain_text_splitters import RecursiveCharacterTextSplitter

class SplitterStructure(object):
    def __init__(self) -> None:
        self.base_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=200)
    
    def split_documents(self, doc_path):

        parser = DOCXParser()
        parser.parse(doc_path)
                
        triples, _ = get_triples_from_dcx(parser.get_lines_with_meta())
        
        f_root = False
        docs=[]
        level_stack = []
        cur_doc = ""
        for triplet in triples:    
            if isinstance(triplet[0], Header_node):
                if not f_root:
                    f_root=True
                    level_stack.append(triplet[0].text)
                    level_stack.append(triplet[0].text)
                    
                elif triplet[1]=='contains_root':
                    if triplet[2].text not in level_stack:
                        level_stack.pop()
                        level_stack.append(triplet[2].text)
                        
                        # если чанк длинней чем 512, что не помещается в контекст, то давайте 
                        if len(cur_doc)>1000:
                            cur_documents = self.create_documents_split(cur_doc, level_stack)
                            for cur_doc in cur_documents:
                                docs.append(cur_doc)
                        else:
                            docs.append(Document(page_content=cur_doc))
                        
                        #print(cur_doc)
                        #print(30*'-')
                        cur_doc=""
                        
                
                if isinstance(triplet[2], Paragraph_node):
                    if cur_doc=="":
                        cur_doc+="Информация из раздела: "
                        cur_doc+="/".join(level_stack)
                    cur_doc+= "\n"
                    cur_doc+= triplet[2].text
        
        return docs
    
    def create_documents_split(self, cur_doc, level_stack):
        res_docs = []
        docs = self.base_splitter.split_text(cur_doc)
        
        for doc in docs:
            res_docs.append(
                Document(page_content= "/".join(level_stack) + "\n" + doc)
            )
            
        return res_docs
        