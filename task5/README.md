# Task 5 — AI Assistant with Tools, Semantic Search and Voice Output

## Overview

Task 5 extends the previous AI assistant by adding a local knowledge base, semantic search, additional tools, audio transcription, text-to-speech, session management, and streaming responses.

The application is a command-line AI assistant based on the OpenAI API. It can answer general questions, use tools when necessary, search information in a local knowledge base, process audio files, generate speech, and save/load conversation sessions.

## Features

- Interactive CLI chat
- OpenAI Responses API
- Function calling
- Mathematical calculations
- Beginner-friendly explanations
- Quiz generation
- Wikipedia search
- Semantic search over a local knowledge base
- Audio transcription
- Text-to-speech output
- Session saving and loading
- Token usage tracking
- Runtime prompt changing
- Adding text and audio documents to the knowledge base
- Streaming assistant responses
- Built-in `/help` command

## Project Structure

```text
task5/
|-- app.py
|-- application.py
|-- task5_chat_session.py
|-- task5_tools.py
|-- task5_tools_schemas.py
|-- task5_semantic_search.py
|-- task5_audio_summary.py
|-- task5_prompts.py
|-- task5_constants.py
|-- text_to_speech.py
|
|-- knowledge/
|   |-- classes.txt
|   |-- inheritance.txt
|   |-- generators.txt
|   |-- ...
|
|-- audio/
|   |-- ...
|
|-- speech/
|   |-- ...
|
|-- session/
    |-- ...
```

````markdown
## Requirements

The project uses Python and the following libraries:

- OpenAI
- FAISS
- NumPy
- Rich
- Wikipedia-API
- Pydantic Settings

Install the dependencies:

```bash
pip install -r requirements.txt
````

## Environment Variables

Create a `.env` file and add your OpenAI API key:

```env
API_KEY=your_api_key
```

## Running the Application

Run the application from the repository root:

```bash
python3 -m task5.app
```

To enable voice output:

```bash
python3 -m task5.app --voice
```

## Commands

### `/help`

Displays all available commands.

```text
/help
```

### `/search`

Searches the local knowledge base using semantic similarity.

```text
/search
```

The application creates an embedding for the query, searches the FAISS index, retrieves the three most relevant documents, and uses them as context for the assistant.

Example:

```text
/search
What is inheritance?
```

### `/update_kb_text`

Adds a new text document to the knowledge base.

```text
/update_kb_text
```

The application asks for the document name and its contents. After adding the document, its embedding is created and the FAISS index is updated.

### `/update_kb_audio`

Adds an audio file to the knowledge base.

```text
/update_kb_audio
```

The audio file is transcribed, added to the knowledge base, embedded, and added to the FAISS index.

### `/summarize_session`

Summarizes the current conversation session.

```text
/summarize_session
```

### `/change_prompt`

Changes the additional prompt used by the assistant.

```text
/change_prompt
```

### `/save_session`

Saves the current session as a JSON file in the `session/` directory.

```text
/save_session
```

### `/load_session`

Loads a previously saved session.

```text
/load_session
```

### `/quit`

Exits the application.

```text
/quit
```

## Available Tools

The assistant can use the following tools through function calling:

* `calculate` — performs mathematical calculations.
* `explain` — explains a study topic in beginner-friendly language.
* `generate_quiz` — generates a quiz with a selected difficulty.
* `search_wikipedia` — searches Wikipedia for factual information.
* `semantic_search` — searches the local knowledge base using semantic similarity.
* `summarize_session` — summarizes the current conversation session.

## Semantic Search

The semantic search system uses OpenAI embeddings and FAISS.

The process works as follows:

```text
Knowledge Base
      ↓
Text Documents
      ↓
Document Embeddings
      ↓
FAISS Index
      ↓
User Query
      ↓
Query Embedding
      ↓
Similarity Search
      ↓
Top 3 Matches
      ↓
Retrieved Context
      ↓
AI Assistant
      ↓
Final Answer
```

Document and query embeddings are normalized before searching. FAISS uses `IndexFlatIP` with inner product similarity.

## Knowledge Base

The local knowledge base is stored in the `knowledge/` directory.

Each `.txt` file represents a separate document.

Example:

```text
knowledge/
|-- classes.txt
|-- inheritance.txt
|-- generators.txt
|-- functions.txt
|-- dictionaries.txt
|-- ...
```

Documents can be added during runtime using `/update_kb_text` or `/update_kb_audio`.

## Audio Processing

The application can transcribe audio files and add their contents to the knowledge base.

The workflow is:

```text
Audio File
    ↓
Whisper
    ↓
Transcription
    ↓
Knowledge Base
    ↓
Embedding
    ↓
FAISS Index
```

This makes information contained in audio files available through semantic search.

## Text-to-Speech

Voice mode can be enabled with:

```bash
python3 -m task5.app --voice
```

After the assistant generates a response, it is converted to speech and saved as an MP3 file in the `speech/` directory.

```text
speech/
|-- speech.mp3
```

## Session Logging

Sessions are saved as JSON files in the `session/` directory.

A session contains information such as:

```json
{
    "timestamp": "...",
    "model": "gpt-5",
    "prompt": "...",
    "messages": [],
    "tokens": 242,
    "tool_calls": [],
    "commands": []
}
```

The session history separates:

* `messages` — conversation messages
* `tool_calls` — tools executed by the assistant
* `commands` — CLI commands executed by the user
* `tokens` — token usage

## Architecture

### `Application`

Controls the main application loop and connects the different components.

### `ChatSession`

Manages the conversation with the language model, streaming responses, tool calls, and session management.

### `Tool`

Contains the implementations of the available assistant tools.

### `Embeddings`

Creates embeddings for documents and user queries.

### `VectorStore`

Manages the local knowledge base, document embeddings, FAISS index, semantic search, and context creation.

### `Whisper`

Handles audio file loading and transcription.

### `TextToSpeech`

Converts assistant responses into MP3 audio files.

### `TokenCounter`

Tracks token usage.

## Example

A semantic search request can look like this:

```text
Please enter your message or enter `quit` to end your Chat Session: /search

Please enter your message you want to search: What is inheritance?

System: Creating query embedding
System: Top 3 matches:
(1) inheritance.txt: 0.5240
(2) classes.txt: 0.2142
(3) generators.txt: 0.1628

System: Creating context for the query

Assistant:
Based on the provided context, inheritance is an object-oriented
programming mechanism that allows a child class to reuse attributes
and methods from a parent class.
```

## Technologies

* Python
* OpenAI API
* FAISS
* NumPy
* Rich
* Wikipedia API
* Whisper
* JSON
* pathlib

## Goal

The goal of Task 5 is to build a complete CLI AI assistant that combines:

* Function calling
* Semantic search
* Local knowledge retrieval
* Audio transcription
* Text-to-speech
* Session management
* Token tracking
* Streaming responses
* Dynamic knowledge base updates
