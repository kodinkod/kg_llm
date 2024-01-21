# kg_llm

This repository houses a Python project designed for transforming DOCX documents into a knowledge graph. The project follows a modular structure with dedicated modules for document parsing, knowledge graph construction, graph visualization, and utility functions. It is organized to accommodate future features such as building a n-gram database, implementing search functionality, and integrating with a language model (LLM). The project includes a testing suite for ensuring robust functionality. Feel free to explore and contribute to this versatile and extensible knowledge graph project

project_root/
│
├── src/
│   ├── __init__.py
│   ├── parser/
│   │   ├── __init__.py
│   │   └── document_parser.py
│   ├── graph/
│   │   ├── __init__.py
│   │   └── knowledge_graph.py
│   ├── docx_reader.py
│   ├── knowledge_graph_builder.py
│   ├── graph_visualizer.py
│   └── utils/
│       ├── __init__.py
│       └── helper_functions.py
│
├── tests/
│   ├── __init__.py
│   ├── test_parser/
│   │   ├── __init__.py
│   │   └── test_document_parser.py
│   ├── test_graph/
│   │   ├── __init__.py
│   │   └── test_knowledge_graph.py
│   ├── test_docx_reader.py
│   ├── test_knowledge_graph_builder.py
│   ├── test_graph_visualizer.py
│   └── test_utils/
│       ├── __init__.py
│       └── test_helper_functions.py
│
├── data/
│   ├── input/
│   │   └── sample_document.docx
│   └── output/
│       └── knowledge_graph.png
│
├── venv/
│
├── main.py
├── requirements.txt
└── README.md



