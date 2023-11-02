import requests
from bs4 import BeautifulSoup
from datetime import datetime
import PyPDF2
import csv
from csv import writer
import os
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer, util
import spacy
from annotated_text import annotated_text
import shutil
from os import walk
# URL of the website you want to scrape
url = 'http://www.fdic.gov/resources/regulations/federal-register-publications/'

#Main index for the public comment submissions
index = 'index.html'

def GetOpenCommentLinks(url):

    OpenComments = []

    # Send an HTTP GET request to the URL   
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <td> elements with class "info"
        info_cells = soup.find_all('td', class_='info')

        # Iterate through the <td> elements
        for info_cell in info_cells:
            SubmitCommentElement = info_cell.find(string='Submit Comment')
            ReadCommentElement = info_cell.find(string='Read Comments')

            if SubmitCommentElement and ReadCommentElement:
                ReadCommentLink = SubmitCommentElement.find_next('a')

                if ReadCommentLink:
                    OpenComments.append(ReadCommentLink['href'])
        return OpenComments

    else:
        # If the request was not successful, print an error message
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def DownloadPublicComments(url):

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')

        info_cells = soup.find_all('td', class_='info')

        # Iterate through the <td> elements
        for info_cell in info_cells:
            pdf_link = info_cell.find('a', class_='pdficon')

            if pdf_link:
                # Get the URL of the PDF
                pdf_url = pdf_link.get('href')
                # Download the PDF file
                pdf_response = requests.get('https://www.fdic.gov/resources/regulations/federal-register-publications/2023/' + pdf_url)
                # Check if the PDF download was successful (status code 200)
                if pdf_response.status_code == 200:
                    # Save the PDF file locally
                    with open("temp/"+pdf_url, 'wb') as pdf_file:
                        pdf_file.write(pdf_response.content)
                        print("PDF downloaded successfully.")
                else:
                        print(f"Failed to download PDF. Status code: {pdf_response.status_code}")
            else:
                print("No PDF link found under class 'pdficon' in the 'info' cell.")
        else:
            print("No <td> element with class 'info' found on the page.")
    else:
        # If the request was not successful, print an error message
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def DownloadRulePDF(RuleURL):
    # Send an HTTP GET request to the URL
    response = requests.get(RuleURL)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')

        info_cells = soup.find_all('p')

        # Iterate through the <td> elements
        for info_cell in info_cells:
            pdf_link = info_cell.find('a', class_='pdficon')

            if pdf_link:
                # Get the URL of the PDF
                pdf_url = pdf_link.get('href')
                # Download the PDF file
                pdf_response = requests.get(pdf_url)
                # Check if the PDF download was successful (status code 200)
                if pdf_response.status_code == 200:
                    # Save the PDF file locally
                    with open("temp/rule.pdf", 'wb') as pdf_file:
                        pdf_file.write(pdf_response.content)
                        print("PDF downloaded successfully.")
                else:
                        print(f"Failed to download PDF. Status code: {pdf_response.status_code}")
            else:
                print("No PDF link found under class 'pdficon' in the 'info' cell.")
        else:
            print("No <td> element with class 'info' found on the page.")
    else:
        # If the request was not successful, print an error message
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    pdf_text = ""
    with open(pdf_file, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_text += page.extract_text()
    return pdf_text

# Function to convert text to CSV
def text_to_csv(text, csv_file):
    with open(csv_file, 'w', newline='', encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        lines = text.split('\n')
        #add a line to the top of the csv file that says "text"
        csv_writer.writerow(["text"])
        for line in lines:
            csv_writer.writerow([line])

# Load a pre-trained sentence transformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Function to calculate cosine similarity between two sentence embeddings
def calculate_similarity(embedding1, embedding2):
    return util.pytorch_cos_sim(embedding1, embedding2)

# Function to find the most similar sentences between two CSV files
def find_most_similar_sentences(csv_file1, csv_file2, threshold=0.7):
    # Load CSV files into dataframes
    df1 = pd.read_csv(csv_file1)
    df2 = pd.read_csv(csv_file2)

    similar_sentences = []

    for _, row1 in df1.iterrows():
        for _, row2 in df2.iterrows():
            sentence1 = str(row1["text"])  # Replace 'text' with your column name
            sentence2 = str(row2["text"])  # Replace 'text' with your column name

            # Encode sentences to get embeddings
            embedding1 = model.encode(sentence1, convert_to_tensor=True)
            embedding2 = model.encode(sentence2, convert_to_tensor=True)

            # Calculate cosine similarity
            similarity = calculate_similarity(embedding1, embedding2)

            if similarity > threshold:
                similar_sentences.append((sentence1, sentence2, similarity.item()))


    # Sort by similarity score in descending order
    similar_sentences.sort(key=lambda x: x[2], reverse=True)
    return similar_sentences

def get_open_rules(url):
    OpenComments = []

    # Send an HTTP GET request to the URL   
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <td> elements with class "info"
        info_cells = soup.find_all('td', class_='info')

        # Iterate through the <td> elements
        for info_cell in info_cells:
            SubmitCommentElement = info_cell.find(string='Submit Comment')
            ReadCommentElement = info_cell.find(string='Read Comments')

            if SubmitCommentElement and ReadCommentElement:
                ReadCommentLink = SubmitCommentElement.find_next('a')

                if ReadCommentLink:
                    OpenComments.append(ReadCommentLink['href'])
        return OpenComments

    else:
        # If the request was not successful, print an error message
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def get_individual_comments(PublicCommentLink):
    IndividualCommentList = []
    # Send an HTTP GET request to the URL
    response = requests.get(PublicCommentLink)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')

        info_cells = soup.find_all('td', class_='info')

        # Iterate through the <td> elements
        for info_cell in info_cells:
            pdf_link = info_cell.find('a', class_='pdficon')
            if pdf_link:
                IndividualCommentList.append(pdf_link.text)
            else:
                print("No PDF link found under class 'pdficon' in the 'info' cell.")
        else:
            print("No <td> element with class 'info' found on the page.")
    else:
        # If the request was not successful, print an error message
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
    return IndividualCommentList

def download_individual_public_comment(PublicCommentLink, IndividualComment):
    #Send an HTTP GET request tot the URL
    response = requests.get(PublicCommentLink)

    #Check if the request was successful (status code 200)
    if response.status_code == 200:
        #parse the HTML content of the page using beautiful soup
        soup = BeautifulSoup(response.text, 'html.parser')

        info_cells = soup.find_all('td', class_='info')

        # Iterate through the <td> elements
        for info_cell in info_cells:
            pdf_link = info_cell.find('a', class_='pdficon')
            if pdf_link and (pdf_link.text == IndividualComment):
                # Get the URL of the PDF
                pdf_url = pdf_link.get('href')
                # Download the PDF file
                pdf_response = requests.get('https://www.fdic.gov/resources/regulations/federal-register-publications/2023/' + pdf_url)
                # Check if the PDF download was successful (status code 200)
                if pdf_response.status_code == 200:
                    # Save the PDF file locally
                    with open("temp/"+pdf_url, 'wb') as pdf_file:
                        pdf_file.write(pdf_response.content)
                        print("PDF downloaded successfully.")
            else:
                print("No PDF link found under class 'pdficon' in the 'info' cell.")
        else:
            print("No <td> element with class 'info' found on the page.")
    else:
        # If the request was not successful, print an error message
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def display_csv_lines_as_text(file_path):
    df = pd.read_csv(file_path, header=None, encoding='cp1252')
    for row in df.iterrows():
        st.text(row[1])

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

def convert_rule_csv(inputPDF, csv_file):
    dict_sum = {}
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
            dict_sum[page_num] = summary
            csv_writer.writerow([summary])
    return dict_sum

def clear_directory(directory_path):
    try:
        # Remove all files in the directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Remove all subdirectories in the directory
        for subdirectory in os.listdir(directory_path):
            subdirectory_path = os.path.join(directory_path, subdirectory)
            if os.path.isdir(subdirectory_path):
                shutil.rmtree(subdirectory_path)

        print(f"Directory '{directory_path}' has been cleared.")
    except Exception as e:
        print(f"An error occurred while clearing the directory: {str(e)}")

def main():
    clear_directory("\\temp")
    #create variable to hold the main url
    indexHTML = url + index
    
    OpenRules = get_open_rules(indexHTML)

    #working on streamlit
    SelectedRule = st.sidebar.selectbox("Select The Ruleset For the Public Comments", OpenRules)

    GroupToggle = st.sidebar.toggle("Run Analysis on All Comments for Ruleset")
    
    if SelectedRule and not GroupToggle:
        commenturl = 'http://www.fdic.gov/resources/regulations/federal-register-publications/'+SelectedRule
        Comments = get_individual_comments(commenturl)
        IndividualPublicComment = st.sidebar.selectbox("Select the Public Comment Below", Comments)

    RunAnalysis = st.sidebar.button("Run Analysis", type="primary")
    if RunAnalysis and not GroupToggle:
        st.write("running analysis on: ", IndividualPublicComment)
        download_individual_public_comment(commenturl, IndividualPublicComment)
        DownloadRulePDF(commenturl)
        for file in os.listdir("temp"):
            print(file)
            pdf_file = f"temp\{file}"
            csv_file = f"temp\{file}.csv"
            if file != "rule.pdf" and file != "hold.txt":
                pdf_text = extract_text_from_pdf(pdf_file)
                text_to_csv(pdf_text, csv_file)
            elif file == "rule.pdf" and file != "hold.txt":
                convert_rule_csv(pdf_file, "temp\rule.pdf.csv")
        for file in os.listdir("temp\\"):
            if file.lower().endswith('.csv') and file != "rule.pdf.csv":
                csv_file1 = "temp\\"+file
                csv_file2 = "temp\\rule.pdf.csv"
                similarity_threshold = 0.5  # Adjust as needed (might need to increase)
                result = find_most_similar_sentences(csv_file1, csv_file2, similarity_threshold)
                st.header(IndividualPublicComment)
                Commentdf = pd.read_csv(csv_file1, encoding="utf8")
                match = []
                matchlink = []
                for sentence1, sentence2, similarity in result:
                    for row in Commentdf["text"]:
                        if row == sentence1:
                            match.append(row)

                            # Initialize a variable to store the matching key
                            matching_key = None

                            # Iterate through the dictionary items
                            for key, value in dict.items():
                                if value == sentence2:
                                    matchlink.append(key)


                    list = [similarity, sentence1, sentence2]
                    with open('Results.csv', 'a') as f_object:
                        # Pass this file object to csv.writer()
                        # and get a writer object
                        writer_object = writer(f_object)
                    
                        # Pass the list as an argument into
                        # the writerow()
                        writer_object.writerow(list)
                    
                        # Close the file object
                        f_object.close()
                count = 0
                for row in Commentdf['text']:
                    if row in match:
                        annotated_text("",(row, f"Page: {matchlink[count]}"))
                        count += 1
                    else:
                        st.write(row)

                clear_directory("\\temp")

if __name__ == "__main__":
    main()