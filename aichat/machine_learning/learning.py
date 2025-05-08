import logging
from datetime import datetime
from django.db import IntegrityError
from aichat.models import KnowledgeBase, Message
from .nlp_processor import NLPProcessor

# Инициализация логирования
logger = logging.getLogger(__name__)

class LearningModule:
    def __init__(self):
        """
        Инициализация модуля обучения с процессором обработки текста.
        """
        logger.debug("Инициализация LearningModule")
        try:
            self.nlp_processor = NLPProcessor()
        except Exception as e:
            logger.error(f"Ошибка инициализации NLPProcessor в LearningModule: {str(e)}")
            raise

    def update_knowledge_base(self, question, answer, sources=None, confidence=1.0):
        """
        Обновление базы знаний новым парой вопрос-ответ.
        Аргументы:
            question (str): Вопрос для хранения.
            answer (str): Ответ для хранения.
            sources (list): Список источников (опционально).
            confidence (float): Уровень уверенности в ответе.
        Возвращает:
            KnowledgeBase: Обновленный или новый элемент базы знаний, или None при ошибке.
        """
        logger.debug(f"Обновление базы знаний для вопроса: {question}")
        try:
            processed_question = self.nlp_processor.preprocess_text(question)
            logger.debug(f"Обработанный вопрос: {processed_question}")

            # Проверка наличия похожего вопроса
            similar_item = self.nlp_processor.find_similar_question(question, threshold=0.8)
            if similar_item:
                similar_item.usage_count += 1
                similar_item.last_used = datetime.now()
                if confidence > similar_item.confidence_score:
                    similar_item.answer = answer
                    similar_item.confidence_score = confidence
                    similar_item.sources = sources or []
                similar_item.save()
                logger.debug(f"Обновлен элемент KnowledgeBase: {similar_item.id}")
                return similar_item
            else:
                # Создание нового элемента базы знаний, если похожий вопрос не найден
                new_item = KnowledgeBase.objects.create(
                    question_pattern=processed_question,
                    answer=answer,
                    sources=sources or [],
                    confidence_score=confidence
                )
                logger.debug(f"Создан новый элемент KnowledgeBase: {new_item.id}")
                return new_item
        except IntegrityError as e:
            logger.error(f"Не удалось создать/обновить элемент KnowledgeBase: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка в update_knowledge_base: {str(e)}")
            return None

    def learn_from_conversation(self, conversation_id):
        """
        Извлечение знаний из беседы путем поиска пар вопрос-ответ.
        Аргументы:
            conversation_id (int): ID беседы для обучения.
        """
        logger.debug(f"Обучение из беседы {conversation_id}")
        try:
            messages = Message.objects.filter(conversation_id=conversation_id).order_by('created_at')
            logger.debug(f"Найдено {len(messages)} сообщений в беседе")
            for i in range(len(messages) - 1):
                if messages[i].is_user_message and not messages[i + 1].is_user_message:
                    question = messages[i].text
                    answer = messages[i + 1].text
                    sources = messages[i + 1].sources
                    self.update_knowledge_base(question, answer, sources)
        except Exception as e:
            logger.error(f"Ошибка обучения из беседы {conversation_id}: {str(e)}")