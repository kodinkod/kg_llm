import hashlib
import os
import sys
import time
import zipfile
from typing import List

from bs4 import BeautifulSoup

from docx_parser.data_structures.paragraph import Paragraph
from docx_parser.data_structures.paragraph_info import ParagraphInfo
from docx_parser.extractors.numbering_extractor import NumberingExtractor
from docx_parser.extractors.styles_extractor import StylesExtractor


class DOCXParser:

    def __init__(self):
        self.__init_structures()

    def can_parse(self,
                  filename: str) -> bool:
        """
        checks if DOCXParser can parse file with filename path
        :param filename: path to the file for checking
        """
        return filename.endswith(".docx")

    def parse(self,
              filename: str) -> None:
        """
        parses document into paragraphs and runs, extracts text for each run and paragraph and it's metadata
        :param filename: name of the .docx file
        """
        self.__init_structures()
        if not self.can_parse(filename):
            raise ValueError('it is not .docx file')
        with open(filename, "rb") as file_doc:
            file_hash = hashlib.md5()
            chunk = file_doc.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = file_doc.read(8192)
        self.hash = file_hash.hexdigest()

        document = zipfile.ZipFile(filename)
        try:
            self.document_bs = BeautifulSoup(document.read('word/document.xml'), 'xml')
        except KeyError:
            try:
                self.document_bs = BeautifulSoup(document.read('word/document2.xml'), 'xml')
            except KeyError:
                return
        self.styles_extractor = StylesExtractor(BeautifulSoup(document.read('word/styles.xml'), 'xml'))
        try:
            self.numbering_extractor = NumberingExtractor(BeautifulSoup(document.read('word/numbering.xml'), 'xml'),
                                                          self.styles_extractor)
            self.styles_extractor.numbering_extractor = self.numbering_extractor
        except KeyError:
            self.numbering_extractor = None

        # the list of paragraph with their properties
        self.paragraph_list = []
        self.paragraph_xml_list = []

        if not self.document_bs:
            return

        body = self.document_bs.body
        if not body:
            return
        for paragraph in body:
            if paragraph.name == 'tbl':
                continue
            if paragraph.name != 'p':
                # w:docPartGallery w:val="Table of Contents"
                child_paragraph_list = paragraph.find_all('w:p')
                for child_paragraph in child_paragraph_list:
                    self.paragraph_list.append(Paragraph(child_paragraph,
                                                         self.styles_extractor, self.numbering_extractor))
                    self.paragraph_xml_list.append(child_paragraph)
                continue

            self.paragraph_list.append(Paragraph(paragraph, self.styles_extractor, self.numbering_extractor))
            self.paragraph_xml_list.append(paragraph)

    def get_lines(self) -> List[str]:
        """
        :return: list of document's lines
        """
        if self.lines is not None:
            return self.lines
        lines = []
        for paragraph in self.paragraph_list:
            line_text = ""
            for run in paragraph.runs:
                line_text += run.text
            lines.append(line_text)
        self.lines = lines
        return lines

    def get_lines_with_meta(self) -> List[dict]:
        """
        :return: list of dictionaries for each paragraph
        [{"text": "",
        "uid": "line unique identifier",
        "type": ""("paragraph" ,"list_item", "raw_text", "style_header"), "level": (1,1) or None (hierarchy_level),
        "annotations": [("size", start, end, size), ("bold", start, end, True), ...] } ]
        start, end - character's positions begin with 0, end isn't included
        """
        if self.lines_with_meta is not None:
            return self.lines_with_meta
        lines_with_meta = []
        for paragraph in self.paragraph_list:
            paragraph_properties = ParagraphInfo(paragraph)
            line_with_meta = paragraph_properties.get_info()
            if line_with_meta['text']:
                line_with_meta['uid'] = f"{self.hash}_{line_with_meta['uid']}"
                lines_with_meta.append(line_with_meta)
        self.lines_with_meta = lines_with_meta
        return lines_with_meta

    @property
    def get_paragraph_xml_list(self) -> List[BeautifulSoup]:
        return self.paragraph_xml_list

    @property
    def get_document_bs(self) -> BeautifulSoup:
        return self.document_bs

    def __init_structures(self):
        self.document_bs = None
        self.styles_extractor = None
        self.numbering_extractor = None
        # the list of paragraph with their properties
        self.paragraph_list = []
        self.paragraph_xml_list = []
        self.lines_with_meta = None
        self.lines = None
        self.hash = None


if __name__ == "__main__":
    test_dir = '../examples/test/docx'
    # examples_dir = '../examples'
    examples_dir = '/Users/anastasiabogatenkova/Downloads/'
    choice = input('')
    if choice == "test":
        filenames = os.listdir(test_dir)
    else:
        filenames = [choice]
    global_start = time.time()
    start = time.time()
    parser = DOCXParser()
    i = 0
    with open("../examples/test/results.txt", "w") as write_file:
        for filename in filenames:
            try:
                i += 1
                if choice == "test":
                    if parser.can_parse(os.path.join(test_dir, filename)):
                        parser.parse(os.path.join(test_dir, filename))
                    else:
                        continue
                else:
                    if parser.can_parse(os.path.join(examples_dir, choice)):
                        parser.parse(os.path.join(examples_dir, choice))
                    else:
                        continue
                lines_info = parser.get_lines_with_meta()
                if choice != "test":
                    file = sys.stdout
                else:
                    file = write_file
                    print(f"\n\n\n\n\n{filename}\n\n\n", file=file)
                for line in lines_info:
                    print(line['text'], file=file)
                    print(f"Annotations: {line['annotations']}", file=file)

                if choice == 'test':
                    print(f"\r{i} objects are processed...", end='', flush=True)
                if i % 100 == 0:
                    end = time.time()
                    print(f"current time for docs processing = {end - start}")
                    start = end
            except ValueError as err:
                print("ValueError: ", err)
                print(filename)
            except KeyError as err:
                print("KeyError: ", err)
                print(filename)
            except zipfile.BadZipFile:
                pass

# /Users/anastasiabogatenkova/Downloads/1.docx
