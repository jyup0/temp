import requests
from bs4 import BeautifulSoup
import PyPDF2
import csv
from csv import writer
import os
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer, util
import spacy

def CleanRule(Rule):
    # Split the string by "/"
    parts = Rule.split("/")
    # Take the first part and split it by ".html"
    result = parts[1].split(".html")[0]
    return result

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
            summarized_text = summarized_text.replace('\n', ' ')
            summarized_pages.append(summarized_text)

    return summarized_pages

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to summarize text
def summarize_text(text):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

    # Summarize by selecting a subset of sentences (e.g., the first 3 sentences)
    summary = " ".join(sentences[:3])

    return summary

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

def GetAnalyzedFiles(DirPath):
    rows_array = []
    DirIPath = DirPath + "/Index/"
    csvFileName = "AnalyzedFiles.csv"
    try:
        with open(DirIPath+csvFileName, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            for row in csv_reader:
                rows_array.extend(row)

    except FileNotFoundError:
        print(f"The specified CSV file '{csvFileName}' was not found.")
    except PermissionError:
        print(f"You don't have permission to access the CSV file '{csvFileName}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return rows_array

def UpdateAnalyzedComments (SelectedRule):
    
    CleanedRule = CleanRule(SelectedRule)
    DirPath = "temp/" + CleanedRule
    DirPCPath = DirPath+"/PublicComments"
    DirIPath = DirPath + "/Index/"
    DirRPath = DirPath + "/Results/"


    AnalyzedFiles = GetAnalyzedFiles(DirPath)
    files = os.listdir(DirPCPath)
    for file in files:
        if file not in AnalyzedFiles and file.lower().endswith('.pdf'):
            print(f"File {file} is being analyzed now")
            #do an analysis
            result = AnalyzeFile(CleanedRule, file, DirPath)
            #add file to end of AnalyzedFiles.csv
            with open(DirIPath+"AnalyzedFiles.csv", 'a', newline='', encoding="utf-8") as csv_file:
                csv_writer = csv.writer(csv_file)
                #add a line to the top of the csv file that says "text"
                csv_writer.writerow([file])
            #add the analyzed results to the index.csv
            with open(DirRPath+file+".csv", 'a', newline='', encoding="utf-8") as csv_file:
                csv_writer = csv.writer(csv_file)
                #add a line to the top of the csv file that says "text"
                for line in result:
                    csv_writer.writerow(line)
            
        elif file in AnalyzedFiles and file.lower().endswith('.pdf'):
            print(f"File {file} has already been analyzed")

# Function to find the most similar sentences between two CSV files
def find_most_similar_sentences(csv_file1, csv_file2, threshold=0.7):
    # Load CSV files into dataframes
    df1 = pd.read_csv(csv_file1)
    df2 = pd.read_csv(csv_file2)

    similar_sentences = []

    # Load a pre-trained sentence transformer model
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

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

# Function to calculate cosine similarity between two sentence embeddings
def calculate_similarity(embedding1, embedding2):
    return util.pytorch_cos_sim(embedding1, embedding2)

def AnalyzeFile (CleanedRule, file, DirPath):
    #Declare Variables
    Rulepdf = DirPath + "/" + CleanedRule + ".pdf"
    Rulecsv = DirPath + "/" + CleanedRule + ".csv"
    RuleConc = DirPath + "/" + CleanedRule + "concat" + ".csv"

    Filepdf = DirPath + "/PublicComments/" + file
    Filecsv = DirPath + "/PublicComments/" + file + ".csv"

    similarity_threshold = 0.5  # Adjust as needed (might need to increase)
    
    #Convert the Rule PDF into a CSV
    convert_rule_csv(Rulepdf, Rulecsv)

    #Convert the input file to a csv
    pdf_text = extract_text_from_pdf(Filepdf)
    text_to_csv(pdf_text, Filecsv)

    #calculate the most similar sentences
    result = find_most_similar_sentences(Filecsv, Rulecsv, similarity_threshold)
    return result

def DownloadRulePDF(RuleURL, SelectedRule):
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
                    pdf_path = f"temp/{SelectedRule}/{SelectedRule}.pdf"
                    with open(pdf_path, 'wb') as pdf_file:
                        pdf_file.write(pdf_response.content)
                        print("PDF downloaded successfully.")
        else:
            print("No <td> element with class 'info' found on the page.")
    else:
        # If the request was not successful, print an error message
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def UpdateRuleDirectory(SelectedRule):
    #first thing is to make sure a directory within /temp for this exists if not then create one with the clean rule name
    CleanedRule = CleanRule(SelectedRule)
    DirPath = "temp/" + CleanedRule
    DirPCPath = DirPath+"/PublicComments"
    DirIPath = DirPath+"/Index"
    DirRPath = DirPath+"/Results"
    if not os.path.exists(DirPath):
        os.makedirs(DirPath)
        print(f'Directory "{DirPath}" created.')
        UpdateRuleDirectory(SelectedRule)
    else:
        #inside the else statement first download the rule document
        commenturl = 'http://www.fdic.gov/resources/regulations/federal-register-publications/'+SelectedRule
        RulePath = commenturl + CleanedRule + ".pdf"
        if not os.path.exists(RulePath):
            DownloadRulePDF(commenturl, CleanedRule)
            print("Rule Downloaded")
        #check to make sure theres a sub folder /PublicComments
        if not os.path.exists(DirPCPath):
            os.makedirs(DirPCPath)
            print(f'Directory "{DirPCPath}" created.')
            UpdateRuleDirectory(SelectedRule)
        if not os.path.exists(DirIPath):
            os.makedirs(DirIPath)
            print(f'Directory "{DirIPath}" created.')
            UpdateRuleDirectory(SelectedRule)
        if not os.path.exists(DirRPath):
            os.makedirs(DirRPath)
            print(f'Directory "{DirRPath}" created.')
            UpdateRuleDirectory(SelectedRule)

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
        # If the request was not successful, print an error message
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
    return IndividualCommentList

def download_individual_public_comment(PublicCommentLink, IndividualComment, DirPCPath):
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
                pdf_response = requests.get('https://www.fdic.gov/resources/regulations/federal-register-publications/2021/' + pdf_url)
                # Check if the PDF download was successful (status code 200)
                if pdf_response.status_code == 200:
                    # Save the PDF file locally
                    cleaned_string = ''.join(char for char in IndividualComment if char.isalpha())
                    cleaned_string = cleaned_string[:50]
                    print(cleaned_string)
                    with open(DirPCPath+ cleaned_string +".pdf", 'wb') as pdf_file:
                        pdf_file.write(pdf_response.content)
                        print("PDF downloaded successfully.")
    else:
        # If the request was not successful, print an error message
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def UpdatePublicComments(SelectedRule):
    CleanedRule = CleanRule(SelectedRule)
    DirPath = "temp/" + CleanedRule
    DirPCPath = DirPath+"/PublicComments/"
    commenturl = 'http://www.fdic.gov/resources/regulations/federal-register-publications/'+SelectedRule
    #get all public comments under the rule and if they are already not in the file structure /temp/SelecetdRule/PublicComments then download them
    OpenComments = get_individual_comments(commenturl)
    print(OpenComments)
    for comment in OpenComments:
        DirComment = DirPCPath + comment + ".pdf"
        if not os.path.exists(DirComment):
            download_individual_public_comment(commenturl, comment, DirPCPath)
            print(f"downloaded comment: {comment}")
        else:
            print("comment already downloaded")

def CleanResults(rule):
    CleanedRule = CleanRule(rule)
    DirPath = "temp/" + CleanedRule
    DirRPath = DirPath+"/Results/"
    DirNPath = DirPath+"/New/"

    for file in os.listdir(DirRPath):
        print(file)
        df = pd.read_csv(DirRPath+file)
        df_new = pd.DataFrame(df.iloc[:, 1])
        df_new = df_new.drop_duplicates()
        df_new.to_csv(DirNPath+file, index=False)



def main():
    #create variable to hold the main url

    # URL of the website you want to scrape
    url = 'http://www.fdic.gov/resources/regulations/federal-register-publications/'

    #Main index for the public comment submissions
    index = 'index.html'
    indexHTML = url + index
    rule = "2021/2021-computer-security-incident-notification-3064-af59.html"
    #this will be the guiless functions
    #1. check if any new rules have been added
    print("Starting Rule: " + rule)
    #UpdateRuleDirectory(rule)
    #UpdatePublicComments(rule)
    #UpdateAnalyzedComments(rule)
    CleanResults(rule)
    print(rule + " Completed!")

if __name__ == "__main__":
    main()