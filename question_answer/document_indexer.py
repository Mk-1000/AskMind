import re
import os
import time
import nltk
import spacy
from PyPDF2 import PdfReader
from docx import Document
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
from openpyxl import load_workbook
from pptx import Presentation

class DocumentSearcher:
    def __init__(self, data_directory):
        self.config = {
            "data_directory": data_directory,
            "elasticsearch_host": "http://localhost:9200"
        }
        self.es = Elasticsearch(self.config["elasticsearch_host"])
        self.nlp = spacy.load("fr_core_news_sm")
        self._download_stopwords()
        self._download_punkt()

    def _download_stopwords(self):
        try:
            stopwords.words("french")
        except LookupError:
            nltk.download('stopwords')

    def _download_punkt(self):
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

    def preprocess_text(self, text):
        clean_text = re.sub('<.*?>', '', text)
        clean_text = re.sub('[^\w\s]', '', clean_text)
        doc = self.nlp(clean_text)
        lemmatized_tokens = [token.lemma_ if token.lemma_ != "-PRON-" else token.text for token in doc]
        tokens = word_tokenize(" ".join(lemmatized_tokens))
        stemmed_tokens = [SnowballStemmer("french").stem(token) for token in tokens]
        filtered_tokens = [token for token in stemmed_tokens if token not in stopwords.words("french")]
        processed_text = " ".join(filtered_tokens)
        return processed_text

    def _get_indexed_files(self):
        if not self.es.indices.exists(index="documents"):
            return set()

        query = {
            "query": {"match_all": {}},
            "size": 10000  # Adjust the size to retrieve all indexed documents if necessary
        }

        response = self.es.search(index="documents", body=query)
        hits = response["hits"]["hits"]

        indexed_files = set()

        for hit in hits:
            source = hit["_source"]
            indexed_files.add(source["file_path"])

        return indexed_files

    def collect_data(self):
        file_paths = self._get_file_paths(self.config["data_directory"])
        indexed_files = self._get_indexed_files()

        documents = self._generate_documents(file_paths, indexed_files)

        start_time = time.time()  # Start measuring the processing time

        self.index_documents(documents)
        end_time = time.time()  # Stop measuring the processing time
        processing_time = end_time - start_time

        if processing_time > 0:
            message = f"Indexing completed. Total time: {processing_time:.2f} seconds."
        else:
            message = "No documents were indexed."

        return message, processing_time

    def _get_file_paths(self, directory):
        file_paths = []

        for root, _, files in os.walk(directory):
            for file in files:
                file_paths.append(os.path.join(root, file))

        return file_paths

    def _extract_text_from_docx(self, file_path):
        doc = Document(file_path)
        text = ""

        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"

        return text.strip()

    def _extract_text_from_xlsx(self, file_path):
        wb = load_workbook(filename=file_path, read_only=True)
        text = ""

        for sheet in wb.sheetnames:
            ws = wb[sheet]

            for row in ws.iter_rows(values_only=True):
                for cell in row:
                    if cell:
                        text += str(cell) + "\n"

        return text.strip()

    def _extract_text_from_pptx(self, file_path):
        prs = Presentation(file_path)
        text = ""

        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"

        return text.strip()

    def _extract_text_from_pdf(self, file_path):
        with open(file_path, "rb") as file:
            pdf = PdfReader(file)
            text = ""

            for page in pdf.pages:
                text += page.extract_text()

        return text.strip()

    def _generate_documents(self, file_paths, indexed_files):
        for file_path in file_paths:
            if file_path not in indexed_files:
                if file_path.endswith(".docx"):
                    document = self._extract_text_from_docx(file_path)
                    yield (file_path, document)
                elif file_path.endswith(".xlsx"):
                    document = self._extract_text_from_xlsx(file_path)
                    yield (file_path, document)
                elif file_path.endswith(".pptx"):
                    document = self._extract_text_from_pptx(file_path)
                    yield (file_path, document)
                elif file_path.endswith(".pdf"):
                    document = self._extract_text_from_pdf(file_path)
                    yield (file_path, document)
                else:
                    print(f"Unsupported file format: {file_path}")
            else:
                print(f"Skipping already indexed file: {file_path}")

    def index_documents(self, documents):
        actions = [
            {
                "_op_type": "index",
                "_index": "documents",
                "_id": i,
                "_source": {
                    "file_path": file_path,
                    "processed_text": self.preprocess_text(text)
                }
            }
            for i, (file_path, text) in enumerate(documents)
        ]

        for success, info in parallel_bulk(self.es, actions, index="documents"):
            if not success:
                print(f"Failed to index document: {info}")

    def preprocess_query(self, query):
        tokens = word_tokenize(query)
        stemmed_tokens = [SnowballStemmer("french").stem(token) for token in tokens]
        filtered_tokens = [token for token in stemmed_tokens if token not in stopwords.words("french")]
        processed_query = " ".join(filtered_tokens)
        return processed_query

    def search_files(self, query):
        processed_query = self.preprocess_query(query)
        processed_query_tokens = processed_query.split()

        body = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"processed_text": token}} for token in processed_query_tokens
                    ],
                    "minimum_should_match": 1  # At least one token should match
                }
            },
            "size": 4  # Return maximum 1000 results
        }

        response = self.es.search(index="documents", body=body)

        hits = response["hits"]["hits"]
        results = []

        for hit in hits:
            source = hit["_source"]
            result = {
                "file_path": source["file_path"],
                "score": hit["_score"]
            }
            results.append(result)

        return results

    def paragraphs_containing_answer(self, file_path, query):
        try:
            processed_query = self.preprocess_query(query)
            processed_query_tokens = processed_query.split()  # Split the processed query into tokens

            if file_path.endswith(".docx"):
                doc = Document(file_path)
                matching_paragraphs = []

                start_time = time.time()  # Start measuring the processing time

                for paragraph in doc.paragraphs:
                    processed_text = self.preprocess_text(paragraph.text.lower())  # Convert processed text to lowercase
                    processed_text_tokens = processed_text.split()  # Split the processed text into tokens

                    # Find the number of query tokens present in the paragraph
                    num_matching_tokens = sum(token in processed_text_tokens for token in processed_query_tokens)

                    if num_matching_tokens > 0:
                        matching_paragraphs.append(paragraph.text)

                end_time = time.time()  # Stop measuring the processing time
                processing_time = end_time - start_time

                matching_paragraphs_str = "\n\n-------------------------\n\n".join(matching_paragraphs)
                return matching_paragraphs_str, processing_time

            elif file_path.endswith(".xlsx"):
                wb = load_workbook(filename=file_path, read_only=True)
                matching_cells = []

                start_time = time.time()

                for sheet in wb.sheetnames:
                    ws = wb[sheet]

                    for row in ws.iter_rows(values_only=True):
                        for cell in row:
                            if cell:
                                processed_text = self.preprocess_text(str(cell).lower())
                                processed_text_tokens = processed_text.split()

                                num_matching_tokens = sum(
                                    token in processed_text_tokens for token in processed_query_tokens)

                                if num_matching_tokens > 0:
                                    matching_cells.append(str(cell))

                end_time = time.time()
                processing_time = end_time - start_time

                matching_cells_str = "\n\n-------------------------\n\n".join(matching_cells)
                return matching_cells_str, processing_time

            elif file_path.endswith(".pptx"):
                prs = Presentation(file_path)
                matching_shapes = []

                start_time = time.time()

                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            processed_text = self.preprocess_text(shape.text.lower())
                            processed_text_tokens = processed_text.split()

                            num_matching_tokens = sum(
                                token in processed_text_tokens for token in processed_query_tokens)

                            if num_matching_tokens > 0:
                                matching_shapes.append(shape.text)

                end_time = time.time()
                processing_time = end_time - start_time

                matching_shapes_str = "\n\n-------------------------\n\n".join(matching_shapes)
                return matching_shapes_str, processing_time

            elif file_path.endswith(".pdf"):
                with open(file_path, "rb") as file:
                    pdf = PdfReader(file)
                    matching_text = []

                    start_time = time.time()

                    for page in pdf.pages:
                        processed_text = self.preprocess_text(page.extract_text().lower())
                        processed_text_tokens = processed_text.split()

                        num_matching_tokens = sum(
                            token in processed_text_tokens for token in processed_query_tokens)

                        if num_matching_tokens > 0:
                            matching_text.append(page.extract_text())

                    end_time = time.time()
                    processing_time = end_time - start_time

                    matching_text_str = "\n\n-------------------------\n\n".join(matching_text)
                    return matching_text_str, processing_time

            else:
                return f"Unsupported file format: {file_path}", 0

        except Exception as e:
            return str(e), 0

#
# data_directory = r"C:\Users\Administrator\Desktop\documents"
# searcher = DocumentSearcher(data_directory)
# # message, indexing_time_process = searcher.collect_data()
#
# # print(message)
#
# query = "DOSILINK va être utilisé par qui"
# results = searcher.search_files(query)
#
# for result in results:
#     matching_paragraphs, processing_time = searcher.paragraphs_containing_answer(result["file_path"], query)
#     print(f"File: {result['file_path']}")
#     print(f"Processing time: {processing_time:.2f} seconds")
#     print("Matching paragraphs:")
#     print(matching_paragraphs)
#     print("-------------------------")