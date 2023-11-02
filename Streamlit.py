import PyPDF2
import spacy
import csv
from csv import writer

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to summarize text
def summarize_text(text):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

    # Summarize by selecting a subset of sentences (e.g., the first 3 sentences)
    summary = " ".join(sentences[:3])

    return summary

# Function to extract and summarize text from each page of a PDF
def summarize_pdf(pdf_path):
    summarized_pages = []

    # Open the PDF file and extract text from each page
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)

        for page_num in range(total_pages):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()

            # Summarize the text from the page
            summarized_text = summarize_text(page_text)
            summarized_pages.append(summarized_text)

    return summarized_pages

# Specify the path to the PDF document
pdf_path = "C:\\Users\\Ethan\\Prototyping\\Temp\\rule.pdf"  # Replace with your PDF file path



def convert_rule_csv(inputPDF, csv_file):
    
    # Specify the path to the PDF document
    pdf_path = inputPDF

    # Extract and summarize text from the PDF
    summarized_pages = summarize_pdf(pdf_path)

    

    with open(csv_file, 'w', newline='', encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        #add a line to the top of the csv file that says "text"
        csv_writer.writerow(["text"])
        # Print the summarized text for each page
        for page_num, summary in enumerate(summarized_pages, start=1):
            print(f"Page {page_num} Summary:")
            print(summary)
            csv_writer.writerow([summary])
            print("\n")

convert_rule_csv(pdf_path, "testing.csv")