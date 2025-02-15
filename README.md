# Pipeline

A high-level interface for building chatbots with RAG (Retrieval-Augmented Generation) capabilities.

## Features

- Multiple RAG implementations:
  - Web content (WebRAG)
  - Python code (PyRAG)
  - Text files (TxtRAG)
  - PDF documents (PdfRAG)
  - JSON data (JsonRAG)
  - Markdown files (MdRAG)
- YouTube caption downloading
- Support for multiple LLM backends (OpenAI, Ollama, LM Studio)
- Conversation history management
- File operations utilities

## Installation

### Recommended: Docker Setup (All Platforms)
```bash
# Build and start containers
docker-compose up --build -d

# Open interactive shell
docker-compose exec pipeline fish
```

### Alternative: Direct Installation (Linux/MacOS)
```bash
# Clone repository
git clone https://github.com/babakbandpey/pipeline.git
cd pipeline

# Create and activate virtual environment
python -m venv env
source env/bin/activate

# Install with development dependencies
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file:
```
OPENAI_API_KEY=your_key_here  # Optional if using Ollama/LM Studio
```

## Usage Examples

### Basic Chat
```python
from pipeline import Chatbot

# Interactive chat session
chatbot = Chatbot(base_url="http://localhost:11434", model="llama3")
print(chatbot.invoke("Hello! How are you?"))
```

### Web Content Analysis
```python
from pipeline import WebRAG

# Analyze web content
rag = WebRAG(
    base_url="http://localhost:11434",
    model="llama3",
    url="https://example.com"
)
print(rag.invoke("What is this page about?"))
```

### YouTube Caption Processing
```python
from pipeline import YouTubeCaptionDownloader

# Download and process captions
downloader = YouTubeCaptionDownloader('./yt')
captions = downloader.download_captions("https://youtube.com/watch?v=...")
```

### Code Analysis
```python
from pipeline import PyRAG

# Analyze Python code
rag = PyRAG(
    base_url="http://localhost:11434",
    model="llama3",
    path="./my_code.py"
)
print(rag.invoke("Explain what this code does"))
```

### Available Commands
- `/exit`: Exit conversation
- `/reset`: Start new conversation
- `/history`: Show conversation history
- `/delete`: Delete messages
- `/summarize`: Summarize conversation
- `/save`: Save history to file
- `/help`: Show commands

## Development

- Python 3.11+
- Run tests: `pytest`
- Lint code: `pylint`
- Format code: `black`
- Type check: `mypy`

### Development Scripts
- `examples/code_guard.py`: Code analysis and security checks
- `examples/readme_writer.py`: Auto-generate README files
- `examples/run.py`: Interactive chat session
- `examples/yt_caption_organizer.py`: Process YouTube captions

## License

MIT License

## Author

Babak Bandpey <bb@cocode.dk>
```
