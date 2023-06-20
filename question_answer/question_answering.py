import logging
<<<<<<< HEAD
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
=======
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering

logger = logging.getLogger(__name__)


class QuestionAnswering:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large")
        self.model = AutoModelForQuestionAnswering.from_pretrained("facebook/bart-large")

        self.nlp = pipeline("question-answering", model=self.model, tokenizer=self.tokenizer)

    def generate_answer(self, context, question):
        try:
            output = self.nlp(question=question, context=context)
            answer = output["answer"]
            confidence = output["score"]
            return answer, confidence
        except Exception as e:
            raise Exception(f"Error generating answer: {str(e)}")


# # Usage example
question_answering = QuestionAnswering()

context = """La Tunisie a connu différentes périodes historiques. Peuplée dès la préhistoire, elle a été le berceau de la brillante civilisation carthaginoise. À partir du ie siècle av. J-C les Romains en firent un des grands producteurs de blé et d'huile d'olive destiné à approvisionner Rome. La Tunisie devenue le royaume des Vandales au moment des grandes migrations de peuples germaniques fut reconquise au début du vie siècle par les Byzantins de Justinien.

Les Arabes s'emparent de la Tunisie dès le milieu du viie siècle, ils y introduisent l'islam. Kairouan devient le centre d'une brillante civilisation musulmane. La Tunisie va subir les divisions politiques et religieuses du monde arabo-musulman. Le plus souvent ses dirigeants tentent d'échapper à l'autorité des califes de Damas, de Bagdad ou du Caire. En 1574, la Tunisie devient une province de l'empire turc ottoman; mais le bey de Tunis parvient à une quasi indépendance. Au xixe siècle, différents beys modernisent le pays, mais endettent fortement la Tunisie.

En 1882, la France impose son protectorat au gouvernement du bey de Tunis. L'économie est modernisée. Mais les nationalistes tunisiens réclament l'indépendance. Pendant la Seconde Guerre mondiale en 1943, la Tunisie est le lieu d'affrontement entre les armées anglo-américaines et l'armée allemande. Après la guerre, l'agitation nationaliste encadrée par le parti Néo-Destour d'Habib Bourguiba reprend. En 1956, la France se retire de Tunisie qui devient indépendante. Le président Bourguiba laïcise le pays en faisant d'importantes réformes de société, mais il impose le parti unique. À partir de 1987, le président Ben Ali continue l'œuvre de Bourguiba. mais progressivement la Tunisie devient un état policier et l'entourage du président s'enrichit en contrôlant l'économie. En janvier 2011 après un mois de manifestations populaires Ben Ali est obligé de quitter la Tunisie."""

question = "qui est arrivé à Tunisie en 1987"

answer, confidence = question_answering.generate_answer(context, question)
print("Answer:", answer)
print("Confidence:", confidence)
>>>>>>> 5894e201baec337ba47f0271668f67775d5039ad
