![image](https://github.com/jyup0/temp/assets/58010127/fadd7f7f-28f4-416e-b5bf-a7672fb2f8ec)

('board risk institution guideline proposed fdic director ', 110), ('fdic institution guideline risk director proposed board ', 110), ('management risk institution board proposed guideline director ', 108), ('guideline board bank institution risk director management ', 107), ('guideline bank board institution risk management director ', 107), ('board guideline bank institution management risk director ', 107), ('risk management board proposed institution guideline bank ', 104), ('guideline bank institution risk board management fdic ', 100), ('guideline bank board institution management fdic risk ', 100)]

'guideline proposed bank board ', 'bank board guideline director ', 'guideline director bank board ', 'guideline bank director board ', 'risk board institution management ', 'board guideline proposed management ', 'board proposal management risk ', 'bank board director guideline ', 'bank fdic board proposal '

[('ignore ', 1560), ('risk board management bank ', 594), ('guideline proposed bank board ', 470), ('bank proposal board director ', 316), ('bank guideline board director ', 285), ('guideline proposed board bank ', 282), ('proposed guideline bank board ', 282), ('board bank director risk ', 249), ('bank fdic board proposal ', 244), ('risk management board 
institution ', 201)]

[('ignore ', 1560), ('oversee oversight operational opportunity ', 234), ('operating opportunity nw new ', 234), ('operational operating opportunity organized ', 234), ('officer oes operation office ', 192), ('one onerous office oes ', 168), ('october nw ofthe organization ', 153), ('opportunity october outcome organization ', 153), ('oversight oversee overuse ozk ', 153), ('nw new office ofstate ', 153)]

[('ignore ', 1560), ('guideline proposed bank board ', 1107), ('risk management institution board ', 532), ('bank proposal fdic community ', 512), ('bank board guideline director 
', 453), ('bank proposal board director ', 399), ('board director bank proposal ', 399), ('board risk institution management ', 399), ('risk board institution management ', 399), 
('guideline board proposed risk ', 396)]

('new management person particularly onerous occ qualified modify largest liability ', 36), ('institution standard fdic proposed board covered risk management 
director guideline ', 20), ('bank board fdic proposal director state guideline law institution corporate ', 14), ('bank board proposed risk director guideline fdic would institution covered ', 13), ('november message pm overall october request monday inﬂaɵon lange rin ', 12), ('office ofstate new nw ofany modify ofspringfield paiticularly orocc message ', 
12), ('board governance proposal director institution bank corporate fdic law state ', 11), ('risk bank board proposed fdic guideline institution would management director ', 11), ('proposed bank fdic board risk institution director guideline would management ', 11)]

('proposed guideline board bank fdic institution risk director management standard ', 274), ('risk proposed board bank director guideline institution fdic management standard ', 274), ('guideline proposed board bank fdic management director risk institution standard ', 274), ('bank board risk proposal director management institution guideline would covered ', 274), ('bank proposed director board guideline risk institution fdic would management ', 269), ('bank proposed board fdic risk guideline institution director would management ', 269), ('risk management institution board proposed guideline would fdic director bank ', 269), ('risk management institution board guideline proposed fdic bank would director ', 269), ('institution standard proposed fdic covered board risk director management guideline ', 254)]


import PyPDF2
from gensim import corpora, models
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import nltk
from sklearn.metrics.pairwise import cosine_similarity
import os
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
nltk.download('stopwords')
nltk.download('wordnet')
# Function to preprocess and tokenize text
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    # Tokenize and remove punctuation
    tokens = [word.lower() for word in word_tokenize(text) if word.isalnum()]

    # Remove stopwords and lemmatize
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]

    return tokens

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

# Function to identify the top N topics using LDA
def identify_top_topics(text, num_topics=10):
    #REMOVE EMPTY TEXT
    text = extract_text_from_pdf(text)
    if text == "":
        text = "ignore"
    # Preprocess text
    tokens = preprocess_text(text)
    # Create a dictionary representation of the documents
    dictionary = corpora.Dictionary([tokens])
    # Create a corpus from the documents
    corpus = [dictionary.doc2bow(tokens)]

    # Train the LDA model
    lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=75)
    # Get the top topics
    top_topics = lda_model.show_topics(num_topics=num_topics, num_words=10, formatted=False)
    return top_topics

def process_directory(directory_path):
    # Get a list of all files in the directory
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

    # Dictionary to store topics for each file
    topics_for_files = {}

    # Loop through each file in the directory
    for file in files:
        file_path = os.path.join(directory_path, file)
        topics = identify_top_topics(file_path)
        topics_for_files[file] = topics

    return topics_for_files

def preprocess_topic(topic):
    # This is a basic example, you might need a more sophisticated preprocessing based on your data
    element1, element2 = topic
    topic_str = ""
    for item in element2:
        topic_str = topic_str + item[0] + " "
    print(topic_str)
    return topic_str

def get_n_most_common_topics(all_topics, n, similarity_threshold=0.3):
    # Flatten the list of topics from all files and preprocess them
    all_topics_flat = [preprocess_topic(topic) for topics in all_topics.values() for topic in topics]

    # Use TF-IDF vectorizer to convert topics to numerical vectors
    vectorizer = TfidfVectorizer()
    topic_vectors = vectorizer.fit_transform(all_topics_flat)

    # Calculate cosine similarity between topic vectors
    similarity_matrix = cosine_similarity(topic_vectors)

    # Dictionary to store the count of each unique topic
    topic_counter = Counter()

    # Loop through each pair of similar topics and update the count
    for i in range(len(all_topics_flat)):
        for j in range(i + 1, len(all_topics_flat)):
            similarity = similarity_matrix[i, j]
            if similarity > similarity_threshold:
                topic_counter[all_topics_flat[i]] += 1
                topic_counter[all_topics_flat[j]] += 1

    # Get the N most common topics
    most_common_topics = topic_counter.most_common(n)

    return most_common_topics

if __name__ == "__main__":
    comment_path = "comment"

    # Identify the top 10 topics
    top_topics = process_directory(comment_path)
    n_most_common_topics = get_n_most_common_topics(top_topics, 10)  # Change 5 to the desired number of topics
    print(n_most_common_topics)
    #if top_topics:
    #    print(top_topics)
    #    # Print the top topics
    #    for topic_num, words in top_topics:
    #        print(f"Topic {topic_num + 1}: {' '.join([word[0] for word in words])}")
