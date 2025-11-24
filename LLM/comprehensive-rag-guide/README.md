# RAG From Scratch

This repository provides a comprehensive, step-by-step guide to building Retrieval Augmented Generation (RAG) applications from scratch. It accompanies the [RAG From Scratch video series](https://www.youtube.com/playlist?list=PLfaIDFEXuae2LXbO1_PKyVJiQ23ZztA0x) by LangChain.

## Overview

Retrieval Augmented Generation (RAG) is a technique used to enhance the accuracy and reliability of generative AI models with facts fetched from external sources. This project breaks down the RAG pipeline into its core components and explores advanced techniques for optimization.

![RAG Overview](rag_detail_v2.png)

## Notebooks

The project is organized into a series of Jupyter notebooks, each covering specific concepts:

| Notebook | Topics Covered |
| :--- | :--- |
| **[01_introduction_basics.ipynb](01_introduction_basics.ipynb)** | Introduction to RAG, Indexing, Retrieval, Generation, LangSmith Tracing. |
| **[02_query_transformations.ipynb](02_query_transformations.ipynb)** | Multi Query, RAG-Fusion, Decomposition, Step Back Prompting, HyDE. |
| **[03_routing_query_construction.ipynb](03_routing_query_construction.ipynb)** | Logical & Semantic Routing, Query Construction for Metadata Filters. |
| **[04_advanced_indexing.ipynb](04_advanced_indexing.ipynb)** | Multi-representation Indexing, RAPTOR, ColBERT. |
| **[05_advanced_retrieval.ipynb](05_advanced_retrieval.ipynb)** | Re-ranking, Corrective RAG (CRAG), Impact of Long Context. |

## Installation

To run these notebooks, you need to install the required dependencies.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd rag-from-scratch
    ```

2.  **Install dependencies:**
    Most notebooks include a cell to install specific requirements, but you can generally install the core libraries with:
    ```bash
    pip install langchain langchain_community langchain_openai chromadb tiktoken
    ```

3.  **Environment Setup:**
    You will need an OpenAI API key. Set it as an environment variable:
    ```bash
    export OPENAI_API_KEY="your-api-key"
    ```
    (Optional) For LangSmith tracing:
    ```bash
    export LANGCHAIN_TRACING_V2=true
    export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
    export LANGCHAIN_API_KEY="your-langchain-api-key"
    ```

## Usage

Launch Jupyter Notebook or JupyterLab to explore the files:

```bash
jupyter notebook
```

Navigate to the desired notebook and run the cells sequentially. Each notebook is self-contained but builds upon concepts from previous ones.

## Concepts

-   **Indexing**: Loading data, splitting it into chunks, and embedding it into a vector store.
-   **Retrieval**: Fetching relevant documents based on a user query.
-   **Generation**: Using an LLM to generate an answer based on the retrieved context.
-   **Query Translation**: Modifying the user's query to improve retrieval (e.g., RAG-Fusion, HyDE).
-   **Routing**: Directing queries to the most appropriate pipeline.
-   **Re-ranking**: Improving the precision of retrieved results.

## License

[MIT](LICENSE)