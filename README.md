# Code Generator Project

A FastAPI web app that generates beginner-friendly code answers using an AI provider. The app includes a browser UI, prompt suggestions, local generation history, copy buttons, and a `/generate` API endpoint.

## Features

- FastAPI backend with Jinja2 templates.
- AI provider support for OpenAI-compatible chat APIs, OpenAI, Groq, and Gemini.
- Clean frontend for entering prompts and viewing generated code.
- Attach a text or code file so the AI can read and analyze its contents.
- Response formatting into Result, Code, Explanation, and Required Libraries sections.
- Browser localStorage history for recent generations.
- Copy all output or copy individual code blocks.

## Project Structure

```text
Code generator Project/
|-- main.py                 # FastAPI app setup, static files, template rendering, router registration
|-- run.py                  # Local development server entry point
|-- requirements.txt        # Python dependencies
|-- .env.example            # Example environment variables
|-- .gitignore              # Git ignore rules
|-- README.md               # Project documentation
|-- models/
|   `-- __init__.py         # Placeholder package for future data models
|-- routes/
|   |-- __init__.py         # Routes package marker
|   |-- generate.py         # POST /generate endpoint
|   |-- auth.py             # Placeholder for future authentication routes
|-- schemas/
|   |-- __init__.py         # Exports schema classes
|   `-- prompt.py           # Prompt request schema
|-- services/
|   |-- __init__.py         # Services package marker
|   |-- ai_service.py       # AI provider selection and generation logic
|   `-- prompt_service.py   # Builds prompt text, including file-analysis prompts
|-- static/
|   |-- css/
|   |   `-- style.css       # App styling
|   `-- js/
|       `-- app.js          # Frontend behavior, file reading, fetch calls, history, rendering
|-- templates/
|   `-- index.html          # Main web page template
`-- utils/
    `-- __init__.py         # Placeholder package for future helpers
```

## Requirements

- Python 3.10 or newer
- An API key for one supported AI provider

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file in the project root. You can copy `.env.example` and replace the placeholder values:

```bash
cp .env.example .env
```

Example configuration:

```env
AI_PROVIDER=openai

OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
OPENAI_BASE_URL=https://api.openai.com/v1

GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

Supported `AI_PROVIDER` values:

- `openai`
- `groq`
- `gemini`

For OpenAI-compatible providers, the service reads:

- `{PROVIDER}_API_KEY`
- `{PROVIDER}_MODEL`
- `{PROVIDER}_BASE_URL`

You can also use generic overrides:

- `MODEL`
- `BASE_URL`

## Run the App

Start the development server:

```bash
python run.py
```

Open the app in your browser:

```text
http://127.0.0.1:8000
```

## Analyze a File

Use the `Attach file` button in the prompt box to select a text or code file. The browser reads the file content locally, adds it to the prompt, and sends it to `/generate` for AI analysis.

You can either:

- Write your own question, such as `Find bugs in this file`.
- Attach a file without a prompt to get a general analysis.

The app does not upload files to separate storage. File content is only included in the generation request.

## API Usage

### Generate Code

Endpoint:

```http
POST /generate
```

Request body:

```json
{
  "prompt": "Write a Python function to reverse a string",
  "file_name": null,
  "file_content": null
}
```

For file analysis, send `file_name` and `file_content`:

```json
{
  "prompt": "Find bugs in this file",
  "file_name": "app.py",
  "file_content": "print('hello')"
}
```

Success response:

```json
{
  "response": "Generated AI response text",
  "mode": "prompt"
}
```

If the prompt is empty or the provider configuration is missing, the API returns an error with a `detail` message.

## How It Works

1. The browser loads `templates/index.html`.
2. Frontend logic in `static/js/app.js` reads any attached text file and sends the prompt to `POST /generate`.
3. `routes/generate.py` validates the request with `schemas/prompt.py`.
4. `services/prompt_service.py` builds either a normal prompt or a file-analysis prompt.
5. `services/ai_service.py` wraps that prompt in a beginner-friendly system prompt.
6. The selected AI provider generates the response.
7. The frontend formats the result into readable sections and stores recent generations in localStorage.

## Notes

- Keep `.env` private and do not commit real API keys.
- `routes/auth.py`, `models/`, and `utils/` are currently placeholders for future features.
- Frontend history is stored only in the user's browser localStorage, not in a database.
