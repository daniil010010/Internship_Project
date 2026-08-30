# Task 3 — AI Assistant with Semantic Search

## Overview

Task 3 extends the AI assistant from the previous tasks by adding a local knowledge base and semantic search using embeddings and FAISS.

The application is a command-line AI assistant that can answer questions using information retrieved from a local knowledge base. It uses OpenAI embeddings to convert documents and user queries into vectors and FAISS to find the most relevant documents.

## Features

- Interactive command-line chat
- OpenAI API integration
- Token usage tracking
- Local knowledge base
- Semantic search
- OpenAI embeddings
- FAISS vector index
- Context-based answers using retrieved documents
- Configurable system prompt
- Rich terminal output
- Reuse of components from Task 1

## Project Structure

```text
task3/
|-- app.py
|-- semantic_search_day3.py
|-- task3_chat_session.py
|-- task3_constants.py
|-- task3_prompts.py
|-- requirements.txt
|
|-- knowledge/
    |-- async.txt
    |-- classes.txt
    |-- data_structures.txt
    |-- dictionaries.txt
    |-- exceptions.txt
    |-- functions.txt
    |-- generators.txt
    |-- inheritance.txt
    |-- lists.txt
    |-- variables.txt
```

Task 3 also uses modules from `task1`, including the base chat session, configuration, prompts, constants, and token counter.

## Requirements

* Python 3.13+
* OpenAI API key
* Task 1 must be available in the project because Task 3 imports several modules from it.

The required external dependencies are listed in:

```text
task3/requirements.txt
```

Install them with:

```bash
pip install -r task3/requirements.txt
```

The project uses:

* `openai` - OpenAI API
* `rich` - terminal output
* `tiktoken` - token counting
* `numpy` - numerical operations
* `faiss-cpu` - vector similarity search
* `pydantic-settings` - loading configuration from `.env`

## Environment Variables

Create a `.env` file in the project root:

```text
api_key=YOUR_OPENAI_API_KEY
```

The API key is loaded through the configuration from Task 1.

## Running the Application

Run Task 3 from the project root as a Python module:

```bash
python3 -m task3.app
```

Running it this way allows Task 3 to correctly import modules from `task1`.

## Semantic Search

The knowledge base contains text files with information about Python programming topics.

When a user sends a question, the application:

1. Creates an embedding for the user's query.
2. Searches the FAISS index for the most relevant documents.
3. Retrieves the corresponding text from the knowledge base.
4. Creates a context from the retrieved documents.
5. Sends the question and context to the AI assistant.
6. Generates an answer based on the provided context.

Example:

```text
Please enter your message or enter `quit` to end your Chat Session: What is inheritance?
```

The semantic search system finds the most relevant document and provides its contents to the assistant as context.

## Knowledge Base

The local knowledge base is stored in:

```text
task3/knowledge/
```

Each `.txt` file represents a separate document.

For example:

```text
knowledge/
|-- classes.txt
|-- inheritance.txt
|-- generators.txt
|-- exceptions.txt
```

The documents are converted into embeddings and stored in the vector index.

## Token Counting

Task 3 uses the token counter inherited from Task 1 to track token usage during conversations and API requests.

## Configuration

The OpenAI API key is loaded using `pydantic-settings`.

The configuration is provided by Task 1:

```python
from task1.config import API_KEY
```

This allows the application to read the API key from the `.env` file without hardcoding it in the source code.

## Main Components

### `app.py`

The main entry point of the application.

It initializes the semantic search system and the chat session and starts the interactive CLI.

### `semantic_search_day3.py`

Contains the vector store and semantic search functionality.

It uses:

* OpenAI embeddings
* NumPy
* FAISS

to create and search the vector index.

### `task3_chat_session.py`

Extends the base chat session from Task 1 and adds functionality related to retrieval-augmented generation.

### `task3_prompts.py`

Contains prompts used by the Task 3 assistant, including the prompt for using retrieved context.

### `task3_constants.py`

Contains constants used by the semantic search system, such as the embedding model.

## Example Workflow

```text
User question
      |
      |
Create query embedding
      |
      |
Search FAISS index
      |
      |
Retrieve relevant documents
      |
      |
Create context
      |
      |
Send context + question to OpenAI
      |
      |
Generate answer
```

## Example

```text
User: What is a Python generator?

System: Creating query embedding
System: Top matches:
(1) generators.txt
(2) functions.txt
(3) classes.txt

System: Creating context

Assistant:
A generator is a Python function that produces values lazily using
the yield keyword...
```

## Notes

Task 3 is designed to run as part of the overall internship project and depends on reusable components from Task 1.

The `.venv` directory should not be committed to Git. Dependencies should be installed using `requirements.txt`.

