# Multi-turn CLI Chat

## Description

This project is a command-line chatbot built with the OpenAI API.

The application supports multi-turn conversations, custom system prompts, token tracking, conversation summaries and JSON logging.

---

## Features

- Multi-turn chat session
- Streaming responses
- Token counting
- JSON conversation logs
- Custom system prompt (`--prompt`)
- Conversation summary
- Error handling
- Configuration using Pydantic Settings
- Colored terminal output using Rich

---

## Structure

```text
Task 1/
|- app.py
|- chat_session.py
|- config.py
|- constants.py
|- prompts.py
|- schemas.py
|- requirements.txt
|- logs/
|- README.md
```

---

## Installation

Install the required dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project directory:

```env
API_KEY=your_openai_api_key
```

---

## Usage

Run the application with the default system prompt:

```bash
python3 app.py
```

Run the application with a custom system prompt:

```bash
python3 app.py --prompt "Your system prompt"
```

Enter messages in the terminal to communicate with the assistant.

To end the chat session, enter:

```text
/quit
```

---

## Token Tracking

The application uses `tiktoken` to calculate input, output and total token usage.

Token statistics are displayed during the chat session and saved to the conversation log.

---

## Conversation Logs

When the chat session is ended with `/quit`, the conversation is saved as a JSON file in the `logs/` directory.

Each log contains:

- Timestamp
- System prompt
- Conversation history
- Token statistics
- Conversation summary

---

## Error Handling

The application handles common OpenAI API errors, including:

- API connection errors
- API timeout errors
- Authentication errors
- Bad request errors
- Rate limit errors
- API status errors

---

## Configuration

The application uses Pydantic Settings to load the OpenAI API key from the `.env` file.

The API key is provided through the `API_KEY` environment variable.

---

## Technologies

- Python
- OpenAI API
- Pydantic
- Pydantic Settings
- tiktoken
- Rich