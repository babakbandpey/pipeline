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

Choose the appropriate installation method based on your needs:

### Using Pipeline in Your Project

This is the recommended method when using Pipeline as a dependency in your project:

1. Install from GitHub:
```bash
pip install git+https://github.com/babakbandpey/pipeline.git
```

2. Or add to requirements.txt:
```text
git+https://github.com/babakbandpey/pipeline.git
```

This installs:
- Core Pipeline package with all RAG implementations
  - WebRAG: Web content analysis
  - PyRAG: Python code analysis
  - TxtRAG: Text file processing
  - PdfRAG: PDF document analysis
  - JsonRAG: JSON data processing
  - MdRAG: Markdown file analysis
- Utility modules
  - FileUtils: File operations
  - ChatbotUtils: Chatbot helpers
  - PipelineUtils: Configuration tools

Dependencies:
- langchain and related packages
- openai (optional)
- chromadb for vector storage
- other utility packages

### Development Setup with Docker

Use this setup when:
- Developing Pipeline itself
- Running Pipeline as a standalone service
- Contributing to the project

Benefits:
- Isolated development environment
- Consistent dependencies across platforms
- Integrated Git and SSH configuration
- Hot-reloading for development

1. Clone the repository:
```bash
# Clone repository
git clone https://github.com/babakbandpey/pipeline.git
cd pipeline
```

2. Copy and configure environment:
```bash
cp .env-demo .env
# Edit .env with your settings
```

3. Run development setup:
```bash
# Run setup script (first time and after pulling updates)
chmod +x dev.sh
./dev.sh
```

The setup script will:
- Check/create .env file
- Configure SSH for multiple GitHub accounts
- Build and start Docker containers
- Install package in development mode
- Configure Git settings
- Open interactive shell

### Git Configuration for Multiple Accounts

1. Define Git and SSH settings in `.env`:
```bash
# Git Config
GIT_AUTHOR_NAME=Your Name
GIT_AUTHOR_EMAIL=your@email.com
GIT_SSH_KEY_WORK=~/.ssh/id_rsa_work      # Work SSH key path
GIT_SSH_KEY_PERSONAL=~/.ssh/id_rsa_personal  # Personal SSH key path
GIT_SSH_HOST_WORK=github.com-work        # SSH config host for work
GIT_SSH_HOST_PERSONAL=github.com-personal # SSH config host for personal
```

2. SSH config will be auto-generated from .env settings
```bash
# Generated ~/.ssh/config
Host ${GIT_SSH_HOST_WORK}
    HostName github.com
    User git
    IdentityFile ${GIT_SSH_KEY_WORK}
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
