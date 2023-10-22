import os
import glob
import dotenv
import logging
import nltk
import openai
from tqdm import tqdm
from PyPDF2 import PdfReader
from docx import Document

# Constants and Configuration
logging.basicConfig(filename='error_log.txt', level=logging.DEBUG)
dotenv.load_dotenv()
SAMPLES = os.getenv("SAMPLES")
MODEL = os.getenv("MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PATH = os.getenv("PATH")

openai.api_key = OPENAI_API_KEY

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# File Extraction Functions
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return " ".join(paragraph.text for paragraph in doc.paragraphs)

def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        pdf = PdfReader(file)
        return " ".join(page.extract_text() for page in pdf.pages)

FILE_EXTENSION_TO_FUNCTION = {
    '.pdf': extract_text_from_pdf,
    '.docx': extract_text_from_docx,
}

# File Aggregation
def aggregate_files(directory, extensions):
    files = []
    for ext in extensions:
        files.extend(glob.glob(f'{directory}/**/*{ext}', recursive=True))
    return files

# Main Processing Loop
def main():
    files = aggregate_files('../inputs', ['.md', '.txt', '.pdf', '.docx', '.html'])
    all_content = ""

    for file in files:
        ext = os.path.splitext(file)[1]
        content = FILE_EXTENSION_TO_FUNCTION.get(ext, lambda x: open(x, 'r').read())(file)
        all_content += content

    sentences = nltk.tokenize.sent_tokenize(all_content)
    
    with open("json_format.md", "r") as f:
        instructions = f.read()

    system_message_init = {"role": "system", "content": f"You are an expert ... {instructions}."}
    system_message_rest = {"role": "system", "content": f"Reminder: {instructions}"}
    user_message_init = {"role": "user", "content": "The loop will now commence."}

    with open('../outputs/annotated.jsonl', 'a') as f:
        for sentence in tqdm(sentences):
            logging.debug(f"Processing sentence: {sentence}")

            system_message = system_message_rest.copy()
            user_message = user_message_init.copy()
            user_message['content'] = f"Here is the next sentence: {sentence}"

            try:
                response = openai.ChatCompletion.create(model=MODEL, messages=[system_message, user_message])
                labeled_text = response.choices[0].message.content
                f.write(labeled_text)
                f.write("\n")
            except Exception as e:
                logging.error(f"Error: {e}, Sentence: {sentence}")
                time.sleep(1)

            logging.debug(f"Finished processing sentence: {sentence}")

if __name__ == "__main__":
    main()
