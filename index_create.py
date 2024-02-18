from whoosh.analysis import StemmingAnalyzer, StopFilter
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
import os

from nltk.corpus import stopwords

stop_words = set(stopwords.words("english"))

# Create a custom analyzer with stemming and stop words removal
custom_analyzer = StemmingAnalyzer() | StopFilter(stoplist=stop_words)

schema = Schema(title=TEXT(stored=True), content=TEXT(analyzer=custom_analyzer))

# Create the index directory if it doesn't exist
if not os.path.exists("index"):
    os.mkdir("index")

# Create an index in the 'index' directory with the defined schema
index = create_in("index", schema)

# Open the index writer
writer = index.writer()


# Function to extract documents from a file
def extract_documents(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Split content into documents based on the delimiter "[["
        documents = content.split("[[")
        for document in documents:
            # Skip empty strings
            if not document.strip():
                continue
            # Try to split each document into title and text using "]]"
            parts = document.split("]]", 1)
            # Check if there are enough parts
            if len(parts) == 2:
                title, text = parts
                writer.add_document(title=title.strip(), content=text.strip())


# Index each file in the directory
directory_path = "wikipagesfull"
for filename in os.listdir(directory_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(directory_path, filename)
        extract_documents(file_path)

# Commit changes and close the writer
writer.commit()
