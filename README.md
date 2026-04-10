# AI-Sec-Assistant
An AI security assistant that uses your API key or a local llm to run network scans
PROCEDURE BELOW
Use this exact flow:

1. Clone the repo:
```bash
git clone https://github.com/Chiagoziem4/AI-Sec-Assistant.git
cd AI-Sec-Assistant
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. (Optional) Run tests:
```bash
python -m pytest tests/ -v
```

5. Run with sample data in rule-only mode (no API needed):
```bash
python main.py --file sample_scan.txt --no-ai --json --markdown
```

6. Run with AI mode:
```bash
python main.py --file sample_scan.txt --json --markdown
```
Then choose at prompt:
- `1` for OpenAI
- `2` for Ollama
- `3` for rules-only

7. If using OpenAI:
- Put your key in `.env` as `OPENAI_API_KEY=...`, or
- choose `1` and enter key when prompted.

8. If using Ollama:
```bash
ollama serve
ollama pull llama3
python main.py --file sample_scan.txt --json --markdown
```
Then choose `2`.

9. Use real scan files:
```bash
sudo nmap -sV -oN live_scan.txt 192.168.1.0/24
python main.py --file live_scan.txt --format nmap --json --markdown
```

10. Check generated reports:
- They are saved in `outputs/` as timestamped `.json` and `.md` files.
