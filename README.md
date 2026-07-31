# Multi_turn CLI Chat

## Description 

This project is a command-line chatbot built with OpenAI API. It uses real-time streaming, token tracking and JSON logging.

---

## Features

- Multi-turn chat session
- Real-time streaming responses
- Token counting (`tiktoken`)
- JSON conversation logs
- Custom system prompt (`--prompt`)
- Conversation summary
- Error handling
- Colored terminal output using `rich`

---

## Structure

```text
task1/
|--app.py
|--chat_session.py
|--logs/
|--README.md
```

---

## Installation

Install the required libraries:

```bash
pip installl openai
pip install python-dotenv
pip install tiktoken
pip install rich
```

Create a `.env` file:

```text
API_KEY=your_openai_api_key
```

---

## Usage

Run with the default system prompt:

```bash
python app.py
```

Run with a custom system prompt:

```bash
pyrhon app.py --prompt "(Your system prompt)"
```

---

## Token Tracking

The program uses `tiktoken` library to calculate input, output and total number of tokens and tokens per message.

---

## Conversation Logs

Every conversation is saved in the `logs` folder as a JSON file.

Each log contains:

- Timestamp
- System prompt
- Conversation history
- Token statistics
- Conversation summary

---

## Error handling

The application handles the following errors:

- APIConnectionError
- APITimeoutError
- AuthenticationError
- BadRequestError
- RateLimitError
- APIStatusError

---

## Technologies

- Python
- OpenAI API
- tiktoken
- python-dotenv
- rich

