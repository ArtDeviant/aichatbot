import logging
from aichat.models import KnowledgeBase
from .nlp_processor import NLPProcessor
from .utils import search_internet

# Инициализация логирования
logger = logging.getLogger(__name__)

class ResponseHandler:
    def __init__(self):
        """
        Инициализация обработчика ответа с процессором обработки текста и статическими ответами.
        """
        logger.debug("Инициализация ResponseHandler")
        try:
            self.nlp_processor = NLPProcessor(load_immediately=False)
        except Exception as e:
            logger.error(f"Ошибка инициализации NLPProcessor: {str(e)}")
            raise
        self.static_responses = {
            "привет": "Привет! Чем могу помочь?"
        }

    def add_response(self, query, response, sources=None):
        """
        Добавление ответа в базу знаний.
        Аргументы:
            query (str): Запрос пользователя.
            response (str): Ответ для хранения.
            sources (list): Список источников (опционально).
        """
        logger.debug(f"Добавление ответа в базу знаний для запроса: {query}")
        try:
            processed_query = self.nlp_processor.preprocess_text(query)
            knowledge_item = KnowledgeBase.objects.filter(question_pattern=processed_query).first()
            if knowledge_item:
                knowledge_item.usage_count += 1
                knowledge_item.save()
                logger.debug(f"Обновлено количество использований в KnowledgeBase для запроса: {query}")
            else:
                KnowledgeBase.objects.create(
                    question_pattern=processed_query,
                    answer=response,
                    confidence_score=0.7,
                    sources=sources or []
                )
                logger.debug(f"Создан новый элемент KnowledgeBase для запроса: {query}")
        except Exception as e:
            logger.error(f"Не удалось добавить ответ в KnowledgeBase для запроса '{query}': {str(e)}")

    def get_trending_response(self, user_input):
        """
        Поиск популярного ответа в базе знаний.
        Аргументы:
            user_input (str): Ввод пользователя.
        Возвращает:
            str: Популярный ответ или None, если не найден.
        """
        logger.debug(f"Поиск популярного ответа для ввода: {user_input}")
        try:
            knowledge_item = self.nlp_processor.find_similar_question(user_input, threshold=0.7)
            if knowledge_item:
                logger.debug(f"Найден популярный ответ: {knowledge_item.answer}")
                return knowledge_item.answer
            logger.debug(f"Популярный ответ для ввода: {user_input} не найден")
            return None
        except Exception as e:
            logger.error(f"Ошибка в get_trending_response для ввода '{user_input}': {str(e)}")
            return None

    def collect_data_via_parsing(self, query, location="Москва"):
        """
        Сбор данных с помощью парсинга результатов поиска.
        Аргументы:
            query (str): Запрос для поиска.
            location (str): Локация по умолчанию для добавления к запросу, если нужно.
        Возвращает:
            list: Список разобранных результатов.
        """
        logger.debug(f"Сбор данных для запроса: {query}")
        try:
            if "найди" in query.lower() and " в " not in query.lower():
                query = f"{query} в {location}"
            results = search_internet(query, use_selenium=False)
            formatted_results = [{
                'text': result.get('snippet', ''),
                'source': result.get('link', ''),
                'title': result.get('title', '')
            } for result in results if 'snippet' in result and result['snippet']]
            logger.debug(f"Собрано {len(formatted_results)} результатов для запроса: {query}")
            return formatted_results
        except Exception as e:
            logger.error(f"Ошибка сбора данных для запроса '{query}': {str(e)}")
            return []

    def validate_response(self, response):
        """
        Проверка качества ответа.
        Аргументы:
            response (str): Ответ для проверки.
        Возвращает:
            bool: True, если ответ валиден, False в противном случае.
        """
        logger.debug(f"Проверка качества ответа: {response}")
        return bool(response and len(response.strip()) >= 5)

    def categorize_input(self, user_input):
        """
        Классификация ввода пользователя как вопрос или действие.
        Аргументы:
            user_input (str): Ввод пользователя.
        Возвращает:
            str: Категория ("вопрос" или "действие").
        """
        logger.debug(f"Классификация ввода: {user_input}")
        try:
            processed_input = self.nlp_processor.preprocess_text(user_input)
            question_keywords = ["что", "почему", "как", "где", "когда", "сколько", "кто", "?", "найди"]
            if any(keyword in processed_input.lower() for keyword in question_keywords):
                logger.debug("Ввод классифицирован как вопрос")
                return "вопрос"
            logger.debug("Ввод классифицирован как действие")
            return "действие"
        except Exception as e:
            logger.error(f"Ошибка классификации ввода '{user_input}': {str(e)}")
            return "вопрос"

    def handle_question(self, user_input):
        """
        Обработка вопроса.
        Аргументы:
            user_input (str): Ввод пользователя.
        Возвращает:
            tuple: Ответ и список источников.
        """
        logger.debug(f"Обработка вопроса: {user_input}")
        trending_response = self.get_trending_response(user_input)
        if trending_response:
            logger.debug(f"Возвращен популярный ответ: {trending_response}")
            return trending_response, []

        collected_data = self.collect_data_via_parsing(user_input)
        if collected_data:
            valid_responses = [item for item in collected_data if self.validate_response(item['text'])]
            if valid_responses:
                answer = "\n".join(f"- {item['title']}: {item['text']}" for item in valid_responses[:3])
                sources = [{'url': item['source'], 'text': item['title']} for item in valid_responses]
                self.add_response(user_input, answer, sources)
                logger.debug(f"Сгенерирован ответ: {answer}")
                return answer, sources
        # Предоставление более конкретного ответа для неконкретных запросов
        if user_input.lower() in ["что нового?", "что нового"]:
            logger.debug("Ввод неконкретный, возвращается уточняющий ответ")
            return "Пожалуйста, уточните, что именно вы хотите узнать о новостях. Например, новости в Москве или новости технологий?", []
        logger.debug("Не удалось найти информацию для вопроса")
        return f"Не удалось найти информацию по запросу '{user_input}'. Попробуйте уточнить.", []

    def handle_action(self, user_input):
        """
        Обработка действия.
        Аргументы:
            user_input (str): Ввод пользователя.
        Возвращает:
            tuple: Ответ и список источников.
        """
        logger.debug(f"Обработка действия: {user_input}")
        if user_input.lower() in self.static_responses:
            logger.debug(f"Возвращен статический ответ: {self.static_responses[user_input.lower()]}")
            return self.static_responses[user_input.lower()], []

        collected_data = self.collect_data_via_parsing(user_input)
        if collected_data:
            valid_responses = [item for item in collected_data if self.validate_response(item['text'])]
            if valid_responses:
                answer = "\n".join(f"- {item['title']}: {item['text']}" for item in valid_responses[:3])
                sources = [{'url': item['source'], 'text': item['title']} for item in valid_responses]
                self.add_response(user_input, answer, sources)
                logger.debug(f"Сгенерирован ответ: {answer}")
                return answer, sources
        logger.debug("Не удалось найти информацию для действия")
        return f"Не удалось найти информацию по запросу '{user_input}'. Попробуйте уточнить.", []

    def process_input(self, user_input, conversation_id=None, user=None):
        """
        Обработка ввода пользователя и генерация ответа.
        Аргументы:
            user_input (str): Ввод пользователя.
            conversation_id (int): ID беседы (опционально).
            user: Объект пользователя (опционально).
        Возвращает:
            dict: Словарь с статусом успеха, ответом, источниками и категорией.
        """
        logger.debug(f"Начало обработки ввода: {user_input}")
        try:
            if not user_input or not isinstance(user_input, str):
                logger.error("Неверный ввод: пусто или не строка")
                return {
                    "success": False,
                    "answer": "Неверный формат запроса",
                    "sources": [],
                    "error": "Invalid input"
                }

            user_input = user_input.strip()
            logger.debug(f"Обработанный ввод: {user_input}")

            category = self.categorize_input(user_input)
            if category == "вопрос":
                answer, sources = self.handle_question(user_input)
            else:
                answer, sources = self.handle_action(user_input)

            logger.debug(f"Обработан ввод '{user_input}' как {category}, ответ: {answer}")
            return {
                "success": True,
                "answer": answer,
                "sources": sources,
                "category": category
            }
        except Exception as e:
            logger.error(f"Ошибка обработки ввода '{user_input}': {str(e)}")
            return {
                "success": False,
                "answer": "Произошла ошибка при обработке запроса",
                "sources": [],
                "error": str(e)
            }