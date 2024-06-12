import uuid
from dataclasses import dataclass


@dataclass
class Base_node:
    def __init__(self, text: str, id: str = str(uuid.uuid4())):
        self.text = text
        self.id = id

    def get_text(self):
        # очистим текст
        # TODO
        return self.text.strip()


@dataclass
class Header_node(Base_node):
    def __init__(self, text: str, level: tuple, id: str):
        super().__init__(text, id)

        self.level = level
        if self.level is None:
            self.level = -1


@dataclass
class Paragraph_node(Base_node):
    def __init__(self, text: str, id: str):
        super().__init__(text, id)


@dataclass
class List_node(Base_node):
    def __init__(self, text: str, id: str):
        super().__init__(text, id)


@dataclass
class Chunk_node(Base_node):
    def __init__(self, text: str, id: str):
        super().__init__(text, id)


@dataclass
class Root_node(Base_node):
    def __init__(self, text: str, level: tuple, id: str):
        super().__init__(text, id)

        self.level = level
        if self.level is None:
            self.level = -1


@dataclass
class PP_node(Base_node):
    def __init__(self, text: str, id: str):
        super().__init__(text, id)
