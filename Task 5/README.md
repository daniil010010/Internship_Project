# Task 4 — Audio Transcription & Summarization

## Description

A CLI-based application that transcribes audio files using OpenAI Whisper
and generates a concise summary of the transcription using a language model.

The application supports:

- `.mp3` audio files
- `.wav` audio files
- `.m4a` audio files
- Audio transcription using `whisper-1`
- Language-model-based summarization
- Processing multiple audio files in one session
- Error handling for OpenAI API errors
- Rich CLI output

## Project Structure

```text
Task 4
|-- app.py
|-- whisper.py
|-- chat_session.py
|-- embeddings.py
|-- tools.py
|-- tool_schemas.py
|-- .env
|-- logs/
|-- audio/
|-- knowledge
```

## Requirements

- Python 3.x
- OpenAI API key

The project uses the following Python libraries:

- `openai`
- `python-dotenv`
- `rich`
- `tiktoken`

## Configuration

Create a `.env` file in the project directory:

```env
API_KEY=your_api_key_here
```

## Usage

Run the application:

```bash
python3 app.py
```

The program will ask for the path to an audio file:

```text
Please enter the path to an audio file
(supported extensions: '.mp3', '.wav' or '.m4a')
or /quit to exit:
```

Enter the path to an audio file, for example:

```text
audio/lecture.mp3
```

The application will:

1. Validate the audio file.
2. Send it to OpenAI Whisper.
3. Display the transcription.
4. Send the transcription to the language model.
5. Generate and display a summary.
6. Wait for another audio file.

Enter `/quit` to exit the application.

## Example

Run the application:

```bash
python3 app.py
```

Enter the path to an audio file:

```text
Please enter the path to an audio file (supported extensions: '.mp3', '.wav' or '.m4a') or /quit to exit: /Users/daniil/Desktop/task1/audio/sample-speech-1m.mp3
```

The application transcribes the audio file using Whisper:

```text
Transcribing: audio/sample-speech-1m.mp3

Transcription:
Welcome to Samplealit.com, a free online resource for downloading sample files in a wide variety of digital formats. Whether you are a software developer testing
file upload functionality, a quality assurance engineer validating media players, a student learning about digital formats, or simply someone who needs a quick test file,
Samplealit provides ready-to-use files that you can download instantly, completely free of charge. In this recording, we will walk you through every aspect of the Samplealit
platform, exploring the formats we offer, the technical details behind each one, and the many ways these test files can be used in your projects and workflows. Let us begin
with image formats. Images are perhaps the most fundamental type of digital media, and Samplealit offers test files in five major image formats, JPEG, PNG, SVG, GIF, and WEB.
Each format has its own strengths, trade-offs, and ideal use cases, and understanding these differences is essential.
```

The transcription is then sent to the language model to generate a concise summary:

```text
Assistant:

- Overview: Samplealit.com is a free online resource for instantly downloading sample files across a wide range of digital formats.
- Intended users: Software developers (file upload testing), QA engineers (media player validation), students (learning formats), and anyone needing quick test files.
- Offering: Ready-to-use files available completely free of charge.
- Recording scope: Walkthrough of the platform’s offerings, technical details of each format, and practical use cases in projects and workflows.
- Starting focus: Image formats—Samplealit provides test files in JPEG, PNG, SVG, GIF, and WEB.
- Key point: Each image format has distinct strengths, trade-offs, and ideal use cases; understanding these differences is important.
```

## Error Handling

The application handles common errors, including:

- File not found
- Unsupported file format
- Connection errors
- Authentication errors
- Rate limit / API quota errors
- Invalid API requests
- Other OpenAI API errors
- Unexpected errors

## Summarization Prompt

The language model is instructed to:

- Summarize the provided audio transcription concisely.
- Extract the main ideas, important facts, conclusions, and key points.
- Do not add information that is not present in the transcription.
- Use clear and structured language.

## Logs

The application saves chat session logs to the `logs/` directory.

The logs contain information about the session, messages, token usage,
and the summarization prompt.

## Technologies

- Python
- OpenAI API
- Whisper
- Rich
- python-dotenv
- tiktoken