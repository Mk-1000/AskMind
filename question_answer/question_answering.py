import logging
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
logger = logging.getLogger(__name__)

class QuestionAnswering:
    def __init__(self):
        # Initialize the tokenizer and model for question answering
        self.tokenizer = AutoTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
        self.model = AutoModelForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
        self.nlp = pipeline("question-answering", model=self.model, tokenizer=self.tokenizer, top_k=1)


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
