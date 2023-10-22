import openai
import markdown
import dotenv
import os
import nltk
import glob
from PyPDF2 import PdfReader
from docx import Document

import time
import logging
from tqdm import tqdm

logging.basicConfig(filename='error_log.txt', level=logging.DEBUG)

# d/l punkt tokenizer
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


# load in variables from .env file
dotenv.load_dotenv()
samples = os.getenv("SAMPLES")
model = os.getenv("MODEL")
openai.api_key = os.getenv("OPENAI_API_KEY")
path = os.getenv("PATH")

# Because Python's open function doesn't work with .pdf or .docx files, we need to convert them to .txt files
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = " ".join(paragraph.text for paragraph in doc.paragraphs)
    return text

def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        pdf = PdfReader(file)
        text = " ".join(page.extract_text() for page in pdf.pages)
    return text

# Get list of all .md, .txt, .pdf, .docx, and html files in 'inputs/' directory and subdirectories
files = []
files.extend(glob.glob('../inputs/**/*.md', recursive=True))
files.extend(glob.glob('../inputs/**/*.txt', recursive=True))
files.extend(glob.glob('../inputs/**/*.pdf', recursive=True))
files.extend(glob.glob('../inputs/**/*.docx', recursive=True))
files.extend(glob.glob('../inputs/**/*.html', recursive=True))

all_content = ""

for file in files:
    if file.endswith('.pdf'):
        content = extract_text_from_pdf(file)
    elif file.endswith('.docx'):
        content = extract_text_from_docx(file)
    else:
        with open(file, "r") as f:
            content = f.read()
    all_content += content

# Split the content into sentences
sentences = nltk.tokenize.sent_tokenize(all_content)



# Read in instructions

with open("json_format.md", "r") as f:
    instructions = f.read()



# Static messages
system_message_init = {"role": "system", "content": f"""You are an expert NLP annotator. You are working on a project to annotate sentences for expanding the range of entities that our NLP model can perform NER (Named Entity Recognition).
                  We are going to enter a loop where I'll feed you a series of strings that have not been processed.  each discrete string should be a full sentence and not contain 1 or 2 words or what clearly looks like bad formatting
                  or white space (use your discretion, remember you are the expert here). Here are the instructions for the requested data format: {instructions}.
                  
                  
                  """}

system_message_rest = {"role": "system", "content": f"""Reminder: Here are the instructions for the requested data format: {instructions}."""}
user_message_init = {"role": "user", "content": "The loop will now commence. "}

# Open JSONL file once
with open('../outputs/annotated.jsonl', 'a') as f:
    # for index 0, send the init message

    system_message = system_message_init.copy()
    user_message = user_message_init.copy()
    user_message['content'] = user_message['content']
    system_message['content'] = system_message['content']
    response = openai.ChatCompletion.create(
        model=f"{model}",
        messages=[system_message, user_message],
    )
    

    for sentence in tqdm(sentences):
        logging.debug(f"Processing sentence: {sentence}")
        system_message = system_message_rest.copy()
        user_message = user_message_init.copy()
        user_message['content'] = f"Here is the next sentence: {sentence}"

        try:
            response = openai.ChatCompletion.create(
                model=f"{model}",
                messages=[system_message, user_message],
            )

            # Extract and write the labeled text
            labeled_text = response.choices[0].message.content
            f.write(labeled_text)
            f.write("\n")

        except Exception as e:
            logging.error(f"Error: {e}, Sentence: {sentence}")
            time.sleep(1)  # wait for 1 second before next request

        logging.debug(f"Finished processing sentence: {sentence}")
