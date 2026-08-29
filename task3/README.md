# Task 3 — Semantic Search / RAG

## Description

A simple semantic search and RAG system for Python-related documents.

The system:
- Loads `.txt` documents from `knowledge/`
- Creates embeddings using `text-embedding-3-small`
- Calculates cosine similarity
- Selects the top 3 relevant documents
- Builds a context
- Generates an answer using the language model

## Technologies

- Python
- OpenAI API
- NumPy
- python-dotenv
- Rich

## Structure

```
Task 3
├── app.py
├── embeddings.py
├── chat_session.py
├── knowledge/
└── README.md
```

## Run

Create a `.env` file:

```
API_KEY=your_api_key
```

Run the application:

```
python3 app.py
```

Enter `/start` and ask a question.

## Example

```text
$ python3 app.py

System prompt: Explain as you can

Please enter the `/start` to start your Chat Session or enter `/quit` to end your Chat Session: /start

System:
Loaded: classes.txt
Loaded: async.txt
Loaded: variables.txt
Loaded: inheritance.txt
Loaded: functions.txt
Loaded: generators.txt
Loaded: dictionaries.txt
Loaded: exceptions.txt
Loaded: lists.txt
Loaded: data_structures.txt

Please enter your message or enter `/quit` to end your Chat Session: What is Python function?

User: What is Python function?

System: Creating query embedding
System: Comparing embeddings
System: Top 3 matches:

(1) functions.txt
(2) variables.txt
(3) exceptions.txt

System: Creating context for the query

Assistant:

A Python function is a reusable block of code designed to perform a particular task. It’s defined with the def keyword, can receive input through parameters (including default values), and can send back a result using return. Functions can be called multiple times from different parts of a program, reducing code duplication and improving maintainability. Python also supports anonymous functions via lambda expressions.
```