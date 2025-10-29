# Java-to-Node.js Analyzer and Converter

**Presentation**: Presentation (ppt) can be found in `Presentation` folder
**Output**: Json output is saved  as `codebase_analysis.json` file
**Converted NodeJs**: Converted NodeJs files are saved under `converted` folder

## Overview
- **Purpose**: Analyze a Java codebase to extract structure (controllers, services, DAOs, models), summarize modules, and generate Node.js equivalents.
- **Architecture**:
  - `analyzer.py` scans the code, uses chunking to break down the code into smaller parts, LLM prompts, and finally converts the code to Node.js.
  - `llm_providers/` supplies pluggable LLM backends (`Gemini` via LangChain, `Ollama` local - tried Ollama but as it is timing out utilized Gemini free tier).
  - Generates a consolidated JSON knowledge base in `codebase_analysis.json` and converted Node.js files and saved in `converted/`. Tried to convert same name files for controllers, services, DAOs.
- **LLM Integration**:
  - Default provider: **Gemini** through `langchain-google-genai` with `ChatGoogleGenerativeAI`.
  - Provider can be swapped (e.g., local `Ollama`).

## Instructions to Run

### 1) Prerequisites
- Python 3.14.0 (Minimum 3.9 required)
- Install dependencies:
```bash
pip install langchain langchain-google-genai
```
### 2) Set your LLM provider

- Using **Gemini (LangChain)**:
  - Set an API key via env var or pass directly.
  - Git Bash (my preference):
    ```bash
    export LLM_PROVIDER=gemini
    export GEMINI_API_KEY=="<your_gemini_api_key>"
    ```
  - PowerShell (if you prefer):
    ```powershell
    $env:llm_provider = "gemini"
    $env:GEMINI_API_KEY = "<your_gemini_api_key>"   # session only
    # or persist (restart terminal after):
    setx GEMINI_API_KEY "<your_gemini_api_key>"
    ```

- Using **Ollama (local)**:
  - if you want to run locally, use Ollama, install Ollama and ensure a model is available (I used `llama3`).
  - Start Ollama service and ensure a model is available (I used `llama3`).
  - No API key is needed.

### 3) Minimal usage example
```
Run it:
```bash
python main.py
```

## Assumptions and Limitations
- **Java project layout**: Assumes conventional Spring-style organization (controllers/services/DAO/entities).
- **Read-only analysis**: Analyzer only reads files; conversion writes output to `converted/` and never overwrites Java sources.
- **LLM non-determinism**: Outputs may vary per run. Prompts enforce JSON-only where needed, but malformed JSON can still occur; analyzer includes basic cleanup.
- **Model support**: `gemini-2.0-flash` is set by default in the provider; if unsupported by your installed `langchain-google-genai`, switch to a compatible model like `gemini-1.5-flash`.
- **Local models (Ollama)**: Quality and token limits depend on the chosen local model; ensure the model is available and server running.
- **Security**: Do not hardcode real API keys in shared code or commit history.

## Token Limits Management
- **Chunking**: Large files are split by class and then by method boundaries in `analyzer.py` (`chunk_code` and `_chunk_by_methods`). This keeps each prompt under a configurable token/character budget.
- **Prompt sizing**: The Gemini provider sets `max_output_tokens=2048` and a low `temperature=0.1` to reduce verbosity and stay within limits.
- **Multi-chunk merge**: When conversions require several chunks, the tool merges requires/imports and bodies while adding a single `module.exports` at the end.
- **Rate spacing**: Light `time.sleep` calls are used to avoid hitting provider rate limits during batch analysis.

## Troubleshooting
- `export: not recognized`: You’re in PowerShell; use `$env:GEMINI_API_KEY = "..."` instead of `export`.
- `model unsupported`: Switch Gemini model to `gemini-1.5-flash`.
- `Empty/invalid JSON`: The analyzer strips code fences and retries parsing; if persistent, rerun with a different model/temperature or reduce file size.

## Repository Structure (key files)
- `analyzer.py` — main workflow.
- `llm_providers/` — pluggable providers (`gemini.py`, `ollama.py`, `base.py`).
- `converted/` — generated Node.js files (created on conversion).
- `codebase_analysis.json` — analysis output.
