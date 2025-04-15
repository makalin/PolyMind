# 🧠 PolyMind

**PolyMind** is a terminal-based multi-agent AI interpreter that allows you to seamlessly interact with various AI models (ChatGPT, Claude, LLaMA, Mistral, Gemini, and more) through a single CLI interface. It supports parallel queries, piped file outputs, agent chaining, aliasing, and formatted history.

## ✨ Features

- 🧑‍💻 **Unified Interface** for multiple AI APIs (OpenAI, Anthropic, Google, custom local agents)
- ⏱️ **Parallel Queries** for multi-agent response aggregation
- 📜 **Command History**, aliases, and shell generation
- 📂 **Pipe Output to Files**, export as Markdown
- 🌐 **Custom Agent Support** for local AI
- 📋 **View, Format, Retry, Clear, Export** queries
- 🧩 **JSON Output**, HTML rendering, and diff comparison

## 🚀 Quick Start

```bash
python polymind.py --agent gpt --prompt "Write a poem about the ocean"
```

### Example with multiple agents

```bash
python polymind.py --agents gpt,claude,mistral --prompt "Explain quantum computing"
```

### View formatted markdown output

```bash
python polymind.py --view last --format markdown
```

## ⚙️ Options

| Flag               | Description                                 |
|--------------------|---------------------------------------------|
| `--agent`          | Choose one agent to run                     |
| `--agents`         | Comma-separated list for parallel runs      |
| `--prompt`         | Prompt string to send                       |
| `--pipe`           | Save output to file                         |
| `--alias`          | Define or run command aliases               |
| `--view`           | View last/any history                       |
| `--format`         | Format output as json, markdown, html       |
| `--shell`          | Generate shell command for response         |
| `--retry`          | Retry last prompt with different agent      |
| `--clear`          | Clear history                               |
| `--export`         | Export all history to markdown              |

## 🔧 Configuration

Edit the `config.json` to add API keys and custom agents.

```json
{
  "openai_api_key": "sk-...",
  "claude_api_key": "sk-...",
  "local_agents": {
    "llama": "http://localhost:11434/api"
  }
}
```

## 📦 Requirements

- Python 3.8+
- `requests`
- `rich`
- `argparse`

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🛠️ Future Features

- Agent chaining (pipe one response into the next)
- UI mode with TUI/Browser
- Auto summary/comparison of agent replies
- Plugins and prompt templates

## 🧑‍💻 Author

Developed by [Mehmet T. AKALIN](https://github.com/makalin) – MIT License.

---

**PolyMind** empowers you to explore diverse AI perspectives in one terminal. Type less, think more.
