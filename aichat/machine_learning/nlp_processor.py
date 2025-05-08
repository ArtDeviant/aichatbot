import logging
import numpy as np
import spacy
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel
from aichat.models import KnowledgeBase

# Инициализация логирования
logger = logging.getLogger(__name__)

# Загрузка модели spaCy для русского текста с обработкой ошибок
try:
    logger.debug("Загрузка модели spaCy 'ru_core_news_sm'")
    nlp = spacy.load('ru_core_news_sm')
except Exception as e:
    logger.error(f"Ошибка загрузки модели spaCy 'ru_core_news_sm': {str(e)}")
    nlp = None

class NLPProcessor:
    def __init__(self, load_immediately=True):
        """
        Инициализация процессора обработки текста с моделями TF-IDF и BERT.
        Аргументы:
            load_immediately (bool): Загружать модели сразу или нет.
        """
        logger.debug("Инициализация NLPProcessor")
        self.tfidf_vectorizer = TfidfVectorizer()
        try:
            logger.debug("Загрузка модели BERT 'bert-base-multilingual-cased'")
            self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
            self.bert_model = BertModel.from_pretrained('bert-base-multilingual-cased')
        except Exception as e:
            logger.error(f"Ошибка загрузки модели BERT: {str(e)}")
            self.bert_tokenizer = None
            self.bert_model = None
        if load_immediately:
            self._init_tfidf()

    def _init_tfidf(self):
        """
        Инициализация векторайзера TF-IDF на основе вопросов из базы знаний.
        """
        try:
            logger.debug("Инициализация TF-IDF векторайзера")
            questions = list(KnowledgeBase.objects.values_list('question_pattern', flat=True))
            if questions:
                self.tfidf_vectorizer.fit(questions)
                logger.debug(f"Векторайзер TF-IDF инициализирован с {len(questions)} вопросами")
            else:
                logger.warning("Вопросы в KnowledgeBase для инициализации TF-IDF не найдены")
                self.tfidf_vectorizer.fit([""])
        except Exception as e:
            logger.error(f"Ошибка инициализации векторайзера TF-IDF: {str(e)}")
            self.tfidf_vectorizer.fit([""])

    def preprocess_text(self, text):
        """
        Предварительная обработка текста с токенизацией, лемматизацией и удалением стоп-слов и пунктуации.
        Аргументы:
            text (str): Текст для обработки.
        Возвращает:
            str: Обработанный текст.
        """
        try:
            if nlp is None:
                logger.warning("Модель spaCy не загружена, используется простая обработка текста")
                return text.lower()
            doc = nlp(text.lower())
            tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
            return ' '.join(tokens)
        except Exception as e:
            logger.error(f"Ошибка обработки текста '{text}': {str(e)}")
            return text.lower()

    def get_tfidf_embedding(self, text):
        """
        Получение вложения TF-IDF для заданного текста.
        Аргументы:
            text (str): Текст для вложения.
        Возвращает:
            sparse matrix: Вложение TF-IDF.
        """
        try:
            processed_text = self.preprocess_text(text)
            return self.tfidf_vectorizer.transform([processed_text])
        except ValueError as e:
            logger.error(f"Ошибка получения вложения TF-IDF для текста '{text}': {str(e)}")
            self._init_tfidf()  # Повторная инициализация при ошибке
            return self.tfidf_vectorizer.transform([processed_text])
        except Exception as e:
            logger.error(f"Ошибка получения вложения TF-IDF для текста '{text}': {str(e)}")
            return None

    def get_bert_embedding(self, text):
        """
        Получение вложения BERT для заданного текста.
        Аргументы:
            text (str): Текст для вложения.
        Возвращает:
            numpy array: Вложение BERT.
        """
        try:
            if self.bert_tokenizer is None or self.bert_model is None:
                logger.warning("Модель BERT не загружена, вложение BERT недоступно")
                return None
            inputs = self.bert_tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
            return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        except Exception as e:
            logger.error(f"Ошибка получения вложения BERT для текста '{text}': {str(e)}")
            return None

    def find_similar_question(self, query, threshold=0.7):
        """
        Поиск похожего вопроса в базе знаний с использованием вложений TF-IDF и BERT.
        Аргументы:
            query (str): Запрос для поиска.
            threshold (float): Порог схожести.
        Возвращает:
            KnowledgeBase: Самый похожий элемент базы знаний или None, если не найден.
        """
        try:
            logger.debug(f"Поиск похожего вопроса для запроса: {query}")
            processed_query = self.preprocess_text(query)
            knowledge_items = KnowledgeBase.objects.all()
            if not knowledge_items:
                logger.debug("База знаний пуста")
                return None

            questions = [item.question_pattern for item in knowledge_items]

            # Использование TF-IDF для начальной фильтрации
            query_vec = self.get_tfidf_embedding(processed_query)
            if query_vec is None:
                logger.warning("Не удалось получить TF-IDF вложение для запроса")
                return None

            question_vecs = self.tfidf_vectorizer.transform(questions)
            similarities = cosine_similarity(query_vec, question_vecs).flatten()
            max_idx = np.argmax(similarities)
            max_similarity = similarities[max_idx]

            # Если схожесть TF-IDF выше порога, возвращаем элемент
            if max_similarity >= threshold:
                logger.debug(f"Найден похожий вопрос с помощью TF-IDF: {questions[max_idx]} (схожесть: {max_similarity})")
                return knowledge_items[max_idx]

            # Если TF-IDF не сработал, пробуем вложения BERT
            query_embedding = self.get_bert_embedding(query)
            if query_embedding is None:
                logger.warning("Не удалось получить BERT вложение для запроса")
                return None

            max_similarity = 0
            best_item = None
            for idx, item in enumerate(knowledge_items):
                item_embedding = self.get_bert_embedding(item.question_pattern)
                if item_embedding is None:
                    continue
                similarity = cosine_similarity([query_embedding], [item_embedding])[0][0]
                if similarity > max_similarity and similarity >= threshold:
                    max_similarity = similarity
                    best_item = item

            if best_item:
                logger.debug(f"Найден похожий вопрос с помощью BERT: {best_item.question_pattern} (схожесть: {max_similarity})")
                return best_item

            logger.debug(f"Похожий вопрос для запроса: {query} не найден")
            return None
        except Exception as e:
            logger.error(f"Ошибка в find_similar_question для запроса '{query}': {str(e)}")
            return None