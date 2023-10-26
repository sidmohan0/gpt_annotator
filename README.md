

# GPT Annotator

## Overview

GPT Annotator is a tool that utilizes GPT models to annotate textual data for Named Entity Recognition (NER). It works with various file formats including `.md`, `.txt`, `.pdf`, `.docx`, and `.html`.

## Features

- Extract text from multiple file formats.
- Tokenize and process sentences using NLTK.
- Generate annotated data suitable for NER tasks. Currently output as JSONL

## Requirements

- Python 3.x
- NLTK
- OpenAI API key
- PyPDF2
- python-docx

## Installation

```bash
# Clone the repository
git clone https://github.com/sidmohan0/gpt_annotator.git

# Install dependencies
pip install -r requirements.txt
```

## Usage

Set up your `.env` file with the following variables:

```
SAMPLES=<SAMPLE_SIZE>
MODEL=<GPT_MODEL_NAME>
OPENAI_API_KEY=<YOUR_API_KEY>
PATH=<YOUR_PATH>
```

Run the main script:

```bash
python main.py
```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License. See [`LICENSE.md`](LICENSE.md) for more details.

---

