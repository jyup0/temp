import pandas as pd
import spacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load pre-trained spaCy model
nlp = spacy.load("en_core_web_sm")

# Read CSV file into a DataFrame
df = pd.read_csv(f'Temp/2021-computer-security-incident-notification-3064-af59/New/IndependentBankersAssociationofTexasChristopherLWi.pdf.csv')  # Replace 'your_file.csv' with the actual filename

df['text'] = df['text'].fillna('')

# Preprocess each row in the CSV
def preprocess_text(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop and token.is_alpha])

df['processed_text'] = df['text'].apply(preprocess_text)

# Preprocess predefined topics
predefined_topics = ['Communication Methods / Proof of Communication', '36-Hour Notice Period', 'Computer Security Incident Actual/Potential Standard',
                           'Service Provider - immediate Notification', 'Implementation Concerns', 'Notification Incident could Standard', 'Bank Service Provider Definition',
                           'Proposed Rule Duplicative/Unnessecary', 'Service Provider Notification of 2 People', 'Good Standing reporting standard'] # Replace with your actual topics
topics = [preprocess_text(topic) for topic in predefined_topics]

# Iterate through each row and compute similarity
matching_topics_list = []

for index, row in df.iterrows():
    document = row['processed_text']
    # Vectorize document and topics
    vectorizer = CountVectorizer().fit_transform([document] + topics)
    similarity_matrix = cosine_similarity(vectorizer)

    # Extract similarity scores for document and topics
    document_similarity = similarity_matrix[0, 1:]

    # Set a threshold and identify matching topics
    threshold = 0.2  # Adjust as needed
    matching_topics = [predefined_topics[i] for i, score in enumerate(document_similarity) if score > threshold]

    matching_topics_list.append(matching_topics)

# Add the matching topics to the DataFrame
df['matching_topics'] = matching_topics_list
df['matching_topics'] = df['matching_topics'].apply(tuple)
values = df['matching_topics'].unique()

# Display or save the results
print(values)
#df.to_csv('output_file.csv', index=False)  # Uncomment this line to save the results to a new CSV file
