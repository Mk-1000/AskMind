# AskMind

# Django Document Search Project

This is a Django project that implements a document search functionality. Users can provide a directory path containing various documents (in DOCX, XLSX, PPTX, or PDF format), and ask questions related to the content of those documents. The system will search for relevant paragraphs in the documents and provide answers to the questions.

## Requirements

To run this project, you need to have the following requirements installed:

- Python (version 3.7 or later)
- Django (version 3.0 or later)
- Elasticsearch (version 7.0 or later)
- PyPDF2
- docx
- openpyxl
- pptx
- spacy
- nltk

You can install the required Python packages by running the following command:

```
pip install -r requirements.txt
```

## Usage

1. Clone the project repository:

```
git clone https://github.com/Mk-1000/AskMind.git
cd django-document-search
```

2. Run Elasticsearch:

Make sure Elasticsearch is running on your system. You can download Elasticsearch from the official website and follow the installation instructions for your operating system.

3. Set up the Django project:

```
python manage.py migrate
python manage.py createsuperuser
```

4. Start the Django development server:

```
python manage.py runserver
```

5. Access the application:

Open your web browser and visit `http://localhost:8000`. You should see the document search interface.

6. Index the documents:

On the web interface, enter the path to the directory containing your documents in the "Documents Path" field. Then click the "Submit" button. The system will collect and index the data from the specified directory. The indexing process may take some time, depending on the size and number of documents.

7. Ask a question:

After the documents are indexed, you can enter a question in the "Question" field and click the "Submit" button. The system will search for relevant paragraphs in the indexed documents and provide the answers to the question, along with other details such as processing times and file paths.

## Project Structure

- `django_document_search/` - Django project settings and configuration.
- `document_search/` - Django app containing the document search functionality.
  - `views.py` - Contains the view functions for handling HTTP requests and rendering templates.
  - `document_indexer.py` - Contains the `DocumentSearcher` class responsible for indexing documents and searching for relevant paragraphs.
  - `question_answering.py` - Contains the `QuestionAnswering` class responsible for generating answers to questions.
- `templates/` - HTML templates for rendering the web interface.
  - `index.html` - The main template that displays the document search interface and search results.
- `static/` - Static files such as CSS stylesheets and images.
- `requirements.txt` - A file containing the required Python packages for the project.

## Notes

- The system currently supports searching for documents in DOCX, XLSX, PPTX, and PDF formats. If you have documents in other formats, the system will skip them.
- The system preprocesses the text content of the documents by removing HTML tags, non-alphanumeric characters, and stopwords. It also performs lemmatization, tokenization, and stemming to improve the search results.
- The system uses Elasticsearch for indexing and searching the documents. You need to have Elasticsearch installed and running for the application to work.
- The search results are sorted by relevance score, with the most relevant paragraphs displayed first.
- The application provides processing times for various steps, including file processing, answer generation, and search processing. These times can help in evaluating the performance of the system.

.

![FireShot Capture 002 - Ask a Question - 127 0 0 1](https://github.com/Mk-1000/AskMind/assets/86926622/c1681e38-85b9-460e-98e1-01c03a1762a3)

