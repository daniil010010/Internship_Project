# AI Chat Assistant with Function Calling

A command-line AI chat assistant built with the OpenAI Responses API. The assistant can automatically choose and execute tools using Function Calling, maintain conversation history, count tokens, summarize chats, and save logs.

## Features

- Interactive chat session
- OpenAI Responses API
- Automatic Function Calling
- Calculator tool
- Wikipedia search tool
- Topic explanation tool
- Quiz generation tool
- Multiple tool calls in a single request
- Conversation summarization
- Token counting
- JSON log export

## Available Tools

### calculate

Evaluates mathematical expressions.

Example:

```
Calculate (5 + 4) * 10
```

---

### explain

Explains a topic in beginner-friendly language.

Example:

```
Explain neural networks.
```

---

### generate_quiz

Creates a quiz on a given topic and difficulty.

Example:

```
Create an easy quiz about Python.
```

---

### search_wikipedia

Retrieves information from Wikipedia.

Example:

```
Look up Alan Turing on Wikipedia.
```

## Installation

Clone the repository:

```bash
git clone <repository_url>
cd project
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```
API_KEY=your_openai_api_key
```

## Usage

Run:

```bash
python app.py
```

You can also provide a custom system prompt:

```bash
python app.py --prompt "You are a helpful programming tutor."
```

Exit the application:

```
/quit
```

## Example

```
User:
Calculate 4*4*5 and search Brawl Stars on Wikipedia.

Assistant:
function_call(calculate)

Result:
80

Assistant:
function_call(search_wikipedia)

Assistant:
Calculation: 80

Wikipedia:
Brawl Stars is a multiplayer online battle arena...
```

## Logs

When the chat ends, a JSON log is saved in the `logs/` directory.

Each log contains:

- timestamp
- system prompt
- conversation history
- tool calls
- token usage
- conversation summary

Example:

```json
{
  "timestamp": "...",
  "messages": [...],
  "tool_calls": [...],
  "tokens": {...},
  "summary": "..."
}
```

## Project Structure

```
project/
|
|-- app.py
|-- chat_session.py
|-- tools.py
|-- tool_schema.py
|-- logs/
|-- .env
|-- README.md
```

## Technologies

- Python 3.13
- OpenAI Responses API
- Rich
- python-dotenv
- Wikipedia API

## Sample Run

The following example demonstrates multiple function calls in a single user request:

```text
$ python app.py --prompt "Explain as Teacher"

System prompt: Explain as Teacher

User: Calculate 4*4*5, explain neural networks, and search Brawl Stars on Wikipedia

Assistant: function_call(calculate)
Assistant: function_call(explain)
Assistant: function_call(search_wikipedia)

Result: 80

Assistant:
Here you go:

- Calculation (4*4*5): 80

- Neural networks (simple explanation):
  Neural networks, in simple terms, are pattern-finders. Instead of following
  hand-written rules, they learn from examples.

  ...

- Wikipedia search: Brawl Stars
  Brawl Stars is a multiplayer online battle arena and hero shooter video game
  developed and published by Finnish video game company Supercell.

User: Can you create a short quiz about Cristiano Ronaldo with medium difficulty?

Assistant: function_call(generate_quiz)

Assistant:
Here’s a short, medium-difficulty quiz on Cristiano Ronaldo:

1. In which year did Cristiano Ronaldo win his first Ballon d’Or?
   Answer: 2008, Manchester United

2. Ronaldo has won top-flight league titles in three different countries.
   Name the countries and corresponding clubs.

3. Whose record did Ronaldo surpass to become the all-time leading men's
   international goalscorer?
   Answer: Ali Daei, in 2021
```

