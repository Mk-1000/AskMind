import logging
import re
import time
from threading import Thread
from django.shortcuts import render
from .document_indexer import DocumentSearcher
from .question_answering import QuestionAnswering
import os
import threading

logger = logging.getLogger(__name__)


def clean_paragraph(paragraph):
    """Clean the given paragraph by replacing characters and removing extra spaces."""
    paragraph = paragraph.replace("\n", " ")
    paragraph = re.sub(r"\s?[\(\[].*?[\)\]]", "", paragraph)
    paragraph = paragraph.replace("<", "").replace(">", "")
    paragraph = re.sub(r"\s+", " ", paragraph)
    paragraph = paragraph.strip()
    paragraph = paragraph.replace("-------------------------", "\n\n-------------------------\n\n")
    return paragraph


def extract_directory_path(file_path):
    """Extract the directory path from the given file path."""
    directory_path = os.path.dirname(file_path)
    return directory_path


def process_paragraph(file_processing_time, file_path, question, indexer, answering, results, found_paragraph):
    """Process a single paragraph and add the result to the results list."""
    result = get_paragraphs(file_processing_time=file_processing_time,
                            file_path=file_path,
                            question=question,
                            indexer=indexer,
                            answering=answering)
    if result:
        results.append(result)
        found_paragraph.set()


def get_paragraphs(file_processing_time, file_path, question, indexer, answering):
    """
    Get relevant paragraphs from the given file path and measure processing time.

    Returns a dictionary containing the relevant paragraphs, answer, confidence,
    processing times, and other details.
    """
    paragraphs, highlight_matching_processing_time = indexer.paragraphs_containing_answer(file_path, question)
    highlight_matching_processing_time = round(highlight_matching_processing_time, 2)

    if paragraphs:
        print(paragraphs)
        paragraphs = clean_paragraph(paragraphs)

        start_time = time.time()  # Start measuring the processing time
        answer_results = []

        answer, confidence = answering.generate_answer(paragraphs, question)

        if not answer or answer == "[CLS]":
            answer = "No answer found."

        answer_result = {
            'Answer': answer,
            'Confidence': round(confidence, 2),
            'Paragraph': paragraphs,
            'highlight_matching_processing_time': highlight_matching_processing_time
        }
        answer_results.append(answer_result)

        end_time = time.time()  # Stop measuring the processing time
        answer_processing_time = round(end_time - start_time, 2)

        result = {
            'Question': question,
            'File_Path': file_path,
            'Paragraphs': answer_results,
            'File_Processing_Time': file_processing_time,
            'Answer_Processing_Time': answer_processing_time
        }
        return result

    return None


def search_question(request):
    if request.method == 'POST':
        documents_path = request.POST.get('documents_path')  # Retrieve the directory path
        question = request.POST.get('question')

        indexer = DocumentSearcher(documents_path)
        message, indexing_time = indexer.collect_data()

        answering = QuestionAnswering()

        start_time = time.time()
        relevant_files = indexer.search_files(question)
        end_time = time.time()
        file_processing_time = round(end_time - start_time, 2)

        results = []
        found_paragraph = False

        if relevant_files:
            thread_list = []
            found_paragraph_event = threading.Event()

            for file in relevant_files:
                if documents_path == extract_directory_path(file['file_path']):
                    thread = Thread(target=process_paragraph,
                                    args=(file_processing_time, file['file_path'], question, indexer, answering, results, found_paragraph_event))
                    thread_list.append(thread)
                    thread.start()

            for thread in thread_list:
                thread.join()

            if not found_paragraph_event.is_set():
                results.append({'Question': question, 'Answer': 'No relevant paragraphs found for the query.'})

            # Sort the results by confidence
            results.sort(key=lambda x: x['Paragraphs'][0]['Confidence'], reverse=True)

            context = {
                'results': results,
                'message': message
            }
            return render(request, 'index.html', context)

    return render(request, 'index.html')
