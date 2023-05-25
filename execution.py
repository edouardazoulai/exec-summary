import openai
import os
import json
import base64
import sys
from pdfgeneratorapi import PDFGenerator
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


with open("questions.json", "r") as f:
    questions = json.load(f)


idea = ""
if len(sys.argv) == 2:
    idea = sys.argv[1]


formatting = "json"

prompt = f"""
Your are building a company. Create a very short executive summary sheet to \
synthesize your idea and share it with others. You need it to recruit \
mentors, advisors, key team members, investors or strategic partners.

You will be provided with a templat in json. This templace contains all the \
questions you will need to answer in order to write this document.
Using the same json columns, write answers to each of those questions \
using a {formatting} format. When you are given subquestions (separated with \
dashes), answer to each question separately and use the same format.

If you are provided with an idea, use it, otherwise, find 5 innovative ideas \
and select the one you think will perform the best. Be specific.

After this is done, add to the json output some characteristics \
(3 words maximum for each in one string) using specifically these columns:\
INDUSTRY, FUNDS_NEEDED, IS_NICHE, HAS_PATENTS.

Add to the output placeholders for the following columns: \
LOCATION, EMPLOYEE_NUMBER, FUNDS_RAISED, EXECUTIVE_TEAM, ADVISORY, CONTACTS, \
FOUNDED.

Finally, give it a name under the column: NAME.

This is the idea: {idea}.
Below are the questions:

{questions}
"""

response = get_completion(prompt)
data = json.loads(response)

logo_prompt = f"""
Design high-end modern logo for this company: {data["NAME"]}. It aims to \
{data["TAGLINE"]}.
"""

logo = openai.Image.create(
    prompt=logo_prompt,
    n=1,
    size="256x256",
    response_format="b64_json",
)

data["LOGO"] = f"data:image/gif;base64,{logo['data'][0]['b64_json']}"

with open("answers.json", "w") as f:
    json.dump(data, f)


pdf_client = PDFGenerator(
    api_key=os.getenv("PDF_GENERATOR_API"),
    api_secret=os.getenv("PDF_GENERATOR_SECRET"),
)
pdf_client.set_workspace(os.getenv("PDF_GENERATOR_WORKSPACE"))

template_id = 658454  # for me

with open("answers.json", "r") as f:
    data = json.load(f)

new_pdf = pdf_client.create_document(
    template_id=template_id,
    data=data,
    document_format="pdf",
    response_format="base64",
)

file_content = base64.b64decode(new_pdf.response)
with open("out.pdf", "wb") as f:
    f.write(file_content)
