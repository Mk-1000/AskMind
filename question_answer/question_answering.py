import logging
import time
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering, T5ForConditionalGeneration, T5Tokenizer

logger = logging.getLogger(__name__)

class QuestionAnswering:
    def __init__(self):
        # Initialize the tokenizer and model for question answering
        self.tokenizer = AutoTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
        self.model = AutoModelForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
        self.nlp = pipeline("question-answering", model=self.model, tokenizer=self.tokenizer, top_k=1)
        self.reformulator = T5ForConditionalGeneration.from_pretrained("t5-base")
        self.tokenizer_reformulator = T5Tokenizer.from_pretrained("t5-base", model_max_length=512)

    def generate_answer(self, context, question):
        """
        Generate an answer to the given question based on the provided context.

        Args:
            context (str): The context or document in which the question is being asked.
            question (str): The question being asked.

        Returns:
            answer (str): The generated answer to the question.
            confidence (float): The confidence score associated with the answer.
        """
        output = self.nlp(question=question, context=context)

        # Check if no answer was found
        if not output['answer']:
            return "No answer found.", 0.0

        answer = output['answer']
        confidence = output['score']
        return answer, confidence


#
# Usage example
question_answering = QuestionAnswering()

context = """Pour planifier une visite médicale, sélectionnez un employé depuis la liste et cliquez sur l’onglet suivi médical, ou bien allez au sous module “suivi médical” et cliquez sur l'icône "Calendrier". Pour afficher les détails d’une visite médicale, cliquez sur l'icône "Ambulance” comme le montre la capture d’écran ci-dessous."""

question = "comment planifier une visite médicale"

start_time = time.time()  # Start measuring the processing time
answer, confidence = question_answering.generate_answer(context, question)
end_time = time.time()  # Stop measuring the processing time
answer_processing_time = round(end_time - start_time, 2)

print("Question:", question)
print("Answer:", answer)
print("Confidence:", confidence)
print("Answer processing time:", answer_processing_time)
