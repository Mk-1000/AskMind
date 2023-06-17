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


# #
# # Usage example
# question_answering = QuestionAnswering()
#
# context = """CONFIGURATION DES PR OFILS UTILISATEURS SUR DOS ILINK. INTRODUCTION DOSILINK va être utilisé par des clients. L’objectif de ce logiciel est de devenir une plateforme de communication entre BIOMEDIQA et ses clients. Les clients auront donc leurs données sur le même serveur. Il faut donc s’assurer qu’un client n’accède pas aux données d’un autre client. Ce cahier des charges a pour objectif de développer des profils utilisateur pour les clients. CREATION DE PROFILS L’objectif est de créer 6 profils clients : - Administrateur BIOME DIQA - Administrateur Client - SRP - MDT - Responsable formation - Cadre ADMINISTRATEUR BIOME DIQA Il a accès à toutes les données. Le profil est déjà existant donc inutile de le créer. ADMINISTRATEUR CLIEN T Il a accès aux modules - RH Gestion des employés - Calendrier - Config. Applicative - Utilisateurs/Sociétés - Utilisateurs - Travailleur s exposés - Formations Il peut tout faire : Lecture, Ecriture, Créer, Supprimer, Exporter. C’est toutefois restreint uniquement sur sa société. Dans la vidéo youtube sur la gestion des droits : https://www.youtube.com/watch?v=kko3L - LeRVA&t=130s Il explique comment faire à 1 :45 environ.
#
# -------------------------
#
#  Toutefois cela implique de recréer des permissions spécifiques pour tous les modules. A voir si la condition ne peut pas être généralisée au niveau des groupes ou des rôles. SRP Accès aux modules : - Travailleurs exposés - Gestion des travailleurs - Lis te des travailleurs - Travailleurs exposés - Gestion des travailleurs - Suivi dosimétrique - Travailleurs exposés - Gestion des travailleurs - Configuration - Travailleurs exposés - Tableau de bord - Suivi dosimétrique Sur ces modules il peut tout faire : Lecture, Ecriture, Créer, Supprimer, Exporter. C’est toutefois restreint uniquement sur sa société. MDP Accès aux modules : - Travailleurs exposés - Gestion des travailleurs - Liste des travailleurs - Travailleurs exposés - Gestion des travailleurs - Sui vi médical - Travailleurs exposés - Gestion des travailleurs - Configuration - Travailleurs exposés - Tableau de bord - Suivi médical Sur ces modules il peut tout faire : Lecture, Ecriture, Créer, Supprimer, Exporter. C’est toutefois restreint uniquement s ur sa société. RESPONSABLE FORMATIO N Accès aux modules : - Travailleurs exposés - Gestion des travailleurs - Liste des travailleurs - Travailleurs exposés - Gestion des travailleurs - Configuration - Travailleurs exposés - Tableau de bord - Formation tra vailleur - Formations Sur ces modules il peut tout faire : Lecture, Ecriture, Créer, Supprimer, Exporter. C’est toutefois restreint uniquement sur sa société. CADRE Accès aux modules : - Travailleurs exposés - Formations Sur ces modules il a accès en Lecture uniquement. C’est restreint uniquement sur sa société.
#
# -------------------------
#
#  CREATION DE L’ENVIRO NNEMENT DE TESTS Créer 3 sociétés : BIOMEDIQA, Client1 et Client2. Créer plusieurs utilisateurs pour chaque profil. Tester que l’administrateur BIOMEDIQA a accès à toutes les données. Les utilisateurs de chaque client n’accède qu’à leurs données et que les consignes pour chaque profil soient respectées."""
#
# question = "DOSILINK va être utilisé par qui"
#
# start_time = time.time()  # Start measuring the processing time
# answer, confidence = question_answering.generate_answer(context, question)
# end_time = time.time()  # Stop measuring the processing time
# answer_processing_time = round(end_time - start_time, 2)
#
# print("Question:", question)
# print("Answer:", answer)
# print("Confidence:", confidence)
# print("Answer processing time:", answer_processing_time)
#
# start_time = time.time()  # Start measuring the processing time
# reformulated_answer = question_answering.reformulate_answer(question=question, answer=answer)
# end_time = time.time()  # Stop measuring the processing time
# reformulate_processing_time = round(end_time - start_time, 2)
#
# print("reformulated_answer:", reformulated_answer)
# print("Answer processing time:", reformulate_processing_time)