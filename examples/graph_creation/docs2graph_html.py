import os
import sys

sys.path.insert(0, os.getcwd())
import hydra
import tqdm
from omegaconf import DictConfig

from docx_parser.document_parser import DOCXParser
from src.docx2graph.from_docx_structure.utils import (build_knowledge_graph,
                                                      draw_graph,
                                                      extract_style,
                                                      get_json_from_graph,
                                                      get_style_level,
                                                      get_triples_from_dcx)

"""
create graph from docx using docx structure and create html graph.
"""


@hydra.main(
    version_base=None, config_path="../../configs/", config_name="docx2graph_html.yaml"
)
def main(cfg: DictConfig):
    for doc_path in tqdm.tqdm(cfg.file_names_for_rag_eval):
        parser = DOCXParser()
        parser.parse(doc_path)
        # проставляем добавленные стили
        for item in parser.get_lines_with_meta():
            item["level"] = get_style_level(extract_style(item["annotations"]))

        triples, _ = get_triples_from_dcx(parser.get_lines_with_meta())
        G = build_knowledge_graph(triples)
        link_data_json = get_json_from_graph(G)

        draw_graph(os.path.basename(doc_path), link_data_json)

    print("Done!")


if __name__ == "__main__":
    main()
