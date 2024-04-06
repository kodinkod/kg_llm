import hashlib
import os
import zipfile
from typing import List

from bs4 import BeautifulSoup

from docx_parser.data_structures.run import Run
from docx_parser.extractors.styles_extractor import StylesExtractor


class DocxTable:
    def __init__(self,
                 xml: BeautifulSoup,
                 styles_extractor: "StylesExtractor") -> None:
        """
        contains information about table properties
        :param xml: BeautifulSoup tree with table properties
        """
        self.xml = xml
        self._uid = hashlib.md5(xml.encode()).hexdigest()
        self.styles_extractor = styles_extractor

    @property
    def uid(self) -> str:
        return self._uid

    def get_cells(self) -> List[List[str]]:
        # TODO w:before
        # tbl tag defines table
        # tr tag defines table row
        # tc tag defines table cell
        result_cells = []

        # delete tables inside tables
        for tbl in self.xml.find_all("w:tbl"):
            tbl.extract()

        if self.xml.tbl:
            return result_cells

        rows = self.xml.find_all("w:tr")
        prev_row = []
        for row in rows:
            cells = row.find_all("w:tc")
            cells_text = []

            cell_ind = 0
            for cell in cells:
                # gridSpan tag describes number of horizontally merged cells
                if cell.gridSpan:
                    grid_span = int(cell.gridSpan["w:val"])
                else:
                    grid_span = 1
                # get text of the cell
                cell_text = self.__get_cell_text(cell)
                # vmerge tag for vertically merged set of cells (or horizontally split cells)
                # attribute val may be "restart" or "continue" ("continue" if omitted)
                if cell.vMerge:
                    value = cell.vMerge.get("w:val", "continue")

                    if value == "continue":
                        cell_text += prev_row[cell_ind]
                # split merged cells
                for span in range(grid_span):
                    cell_ind += 1
                    cells_text.append(cell_text)

            result_cells.append(cells_text)
            prev_row = cells_text

        return result_cells

    def __get_cell_text(self, cell: BeautifulSoup) -> str:
        cell_text = ""
        paragraphs = cell.find_all("w:p")
        for paragraph in paragraphs:
            for run_bs in paragraph.find_all("w:r"):
                run = Run(None, self.styles_extractor)
                run.get_text(run_bs)
                cell_text += run.text
            cell_text += '\n'
        if cell_text:
            cell_text = cell_text[:-1]  # remove \n in the end
        return cell_text

    def __get_table_grid(self, tbl_grid: BeautifulSoup) -> List[int]:
        """
        returns list of column widths in table including all splits
        """
        # tblgrid tag defines all widths of table columns
        # tblgrid contains a list of gridcol - width of each column
        # attribute w in gridcol tag specifies the width of this grid column
        table_grid = []
        for grid_col in tbl_grid:
            table_grid.append(int(grid_col["w:w"]))
        return table_grid

    def __get_table_cell_width(self, tcw: BeautifulSoup, table_width: int, current_width: int = 0) -> int:
        """
        returns position of the next column in Twentieths of a Point
        (sums with previous cell widths)
        """
        # tcw tag describes width of the current cell
        # type attribute may be "auto" (Automatically Determined Width), "dxa" (Width in Twentieths of a Point),
        # "nil" (No Width), "pct" (Width in Percent of Table Width w:w="100%")
        if tcw["w:type"] == "dxa":
            return int(tcw["w:w"])
        elif tcw["w:type"] == "nil" or tcw["w:type"] == "auto":
            return current_width
        elif tcw["w:type"] == "pct":
            # value in percent ends with %
            return current_width + int(table_width / float(tcw["w:w"][:-1]))

    def __get_table_width(self, tblw: BeautifulSoup) -> int:
        """
        returns table width in Twentieths of a Point
        """
        if tblw["w:type"] == "dxa":
            return int(tblw["w:w"])
        elif tblw["w:type"] == "nil" or tblw["w:type"] == "auto":
            return 0
        elif tblw["w:type"] == "pct":
            # value in percent ends with %
            return int(tblw["w:w"][:-1])


if __name__ == "__main__":
    test_dir = "/Users/anastasiabogatenkova/DOCXParser/examples/test/docx"
    # filename = "/Users/anastasiabogatenkova/DOCXParser/examples/merged_cells_example.docx"
    with open("results.txt", "w") as f:
        i = 0
        for filename in os.listdir(test_dir):
            if not filename.endswith(".docx"):
                continue
            filename = os.path.join(test_dir, filename)
            document = zipfile.ZipFile(filename)
            document_bs = BeautifulSoup(document.read('word/document.xml'), 'xml')
            tbls = document_bs.find_all("w:tbl")
            styles_extractor = StylesExtractor(BeautifulSoup(document.read('word/styles.xml'), 'xml'))
            tables = []
            for tbl in tbls:
                table = DocxTable(tbl, styles_extractor)
                tables.append(table.get_cells())
            print(f"\n\n\n{filename}", file=f)
            for table in tables:
                print("\nnew table", file=f)
                for row in table:
                    print(row, file=f)
            i += 1
            print(f"\r{i} objects are processed...", end='', flush=True)
