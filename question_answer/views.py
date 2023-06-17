import logging
import re
import time
from django.shortcuts import render
from .document_indexer import DocumentSearcher
from .question_answering import QuestionAnswering

logger = logging.getLogger(__name__)


def clean_paragraph(paragraph):
    # Replace "\n" with " "
    paragraph = paragraph.replace("\n", " ")
    # Remove symbols until
    paragraph = re.sub(r"\s?[\(\[].*?[\)\]]", "", paragraph)
    # Remove angle brackets
    paragraph = paragraph.replace("<", "").replace(">", "")
    # Remove extra spaces
    paragraph = re.sub(r"\s+", " ", paragraph)
    # Strip leading/trailing spaces
    paragraph = paragraph.strip()

    # Add "\n\n" before and after "-------------------------" separator
    paragraph = paragraph.replace("-------------------------", "\n\n-------------------------\n\n")

    return paragraph



def search_question(request):
    if request.method == 'POST':
        documents_path = request.POST.get('documents_path')
        question = request.POST.get('question')

        # Create an instance of DocumentIndexer
        indexer = DocumentSearcher(documents_path)

        # collect_data and index them in Elasticsearch
        message, indexing_time = indexer.collect_data()
        print(message)
        # Create an instance of QuestionAnswering
        answering = QuestionAnswering()

        start_time = time.time()  # Start measuring the processing time
        # Find relevant files
        relevant_files = indexer.search_files(question)
        end_time = time.time()  # Stop measuring the processing time
        file_processing_time = round(end_time - start_time, 2)

        # Variable to track if any relevant paragraphs were found
        found_paragraph = False
        results = []
        if relevant_files:
            for file in relevant_files:
                print(file['file_path'])
                # Get paragraphs from the relevant file and measure processing time
                paragraphs, highlight_matching_processing_time = indexer.paragraphs_containing_answer(file['file_path'], question)
                highlight_matching_processing_time = round(highlight_matching_processing_time, 2)
                if paragraphs:
                    found_paragraph = True
                    print(paragraphs)
                    paragraphs=clean_paragraph(paragraphs)
                    # Clean the paragraph
                    # paragraphs = clean_paragraph(paragraphs)

                    # Measure the processing time for finding the paragraphs and generating the answer
                    start_time = time.time()  # Start measuring the processing time

                    # Answer the question from each paragraph
                    answer_results = []

                    answer, confidence = answering.generate_answer(paragraphs, question)

                    # Check if the answer is empty or equal to [CLS]
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

                    # Store the results
                    result = {
                        'Question': question,
                        'File_Path': file['file_path'],
                        'Paragraphs': answer_results,
                        'File_Processing_Time': file_processing_time,
                        'Answer_Processing_Time': answer_processing_time
                    }
                    results.append(result)

            if not found_paragraph:
                results.append({'Question': question, 'Answer': 'No relevant paragraphs found for the query.'})

            context = {'results': results}
            return render(request, 'index.html', context)

    return render(request, 'index.html')
