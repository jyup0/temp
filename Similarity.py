import PyPDF2
import csv
import os
import pandas as pd
from sentence_transformers import SentenceTransformer, util

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
    
#look for section cheif and find their teams whos responsibvle for each team

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
                print(similar_sentences)

    # Sort by similarity score in descending order
    similar_sentences.sort(key=lambda x: x[2], reverse=True)    
    return similar_sentences

if __name__ == "__main__":

    # for each file in the folder InProgress loop through and convert to csv
    for file in os.listdir("Documents\InProgress"):
        pdf_file = "Documents\InProgress\\" + file
        csv_file = "Documents\Completed\\" + file + ".csv"
        pdf_text = extract_text_from_pdf(pdf_file)
        text_to_csv(pdf_text, csv_file)

    # After converting all files to csv, convert the rules document in Documents\ProposedRules to csv
    pdf_file = "Documents\ProposedRules\\2023-12187.pdf"
    csv_file = "Documents\ProposedRules\ProposedRules.csv"
    pdf_text = extract_text_from_pdf(pdf_file)
    text_to_csv(pdf_text, csv_file)

    # Then using a hugging face transformer we will compare the ProposedRules.csv to each of the other csv files in the Completed folder
    # then for each file we will return the line number in the csv that has the highest similarity score

    for file in os.listdir("Documents\Completed"):
        csv_file1 = "Documents\Completed\\" + file # Replace with the path to your first CSV file
        csv_file2 = "Documents\ProposedRules\ProposedRules.csv"  # Replace with the path to your second CSV file
        similarity_threshold = 0.7  # Adjust as needed

        result = find_most_similar_sentences(csv_file1, csv_file2, similarity_threshold)

        for sentence1, sentence2, similarity in result:
            print(f"Similarity: {similarity:.2f}")
            print(f"Sentence 1: {sentence1}")
            print(f"Sentence 2: {sentence2}")
            print()