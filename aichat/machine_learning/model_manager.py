import logging
from datetime import datetime
from aichat.models import KnowledgeBase
from .nlp_processor import NLPProcessor
from .learning import LearningModule
from .response_handler import ResponseHandler
from .utils import search_internet

# Инициализация логирования
logger = logging.getLogger(__name__)

class AIModelManager:
    def __init__(self, load_immediately=False):
        """
        Инициализация менеджера модели ИИ с компонентами обработки текста, обучения и генерации ответа.
        Аргументы:
            load_immediately (bool): Загружать модели сразу или нет.
        """
        logger.debug("Инициализация AIModelManager")
        try:
            self.nlp_processor = NLPProcessor(load_immediately=load_immediately)
            self.learning_module = LearningModule()
            self.response_handler = ResponseHandler()
        except Exception as e:
            logger.error(f"Ошибка инициализации AIModelManager: {str(e)}")
            raise

    def search_internet(self, query, location="Москва"):
        """
        Выполнение поиска в интернете по заданному запросу.
        Аргументы:
            query (str): Запрос для поиска.
            location (str): Локация по умолчанию для добавления к запросу, если нужно.
        Возвращает:
            dict: Словарь с статусом успеха, результатами и необработанным ответом.
        """
        logger.debug(f"Поиск в интернете для запроса: {query}")
        try:
            # Добавление локации к запросу, если содержит "найди" и не имеет локации
            if "найди" in query.lower() and " в " not in query.lower():
                query = f"{query} в {location}"
            results = search_internet(query, use_selenium=False)
            answer_snippets = [
                {
                    'source': result.get('link', ''),
                    'text': result.get('snippet', ''),
                    'title': result.get('title', '')
                }
                for result in results
                if 'snippet' in result and result['snippet']
            ]
            logger.debug(f"Поиск в интернете вернул {len(answer_snippets)} выдержек")
            return {
                'success': bool(answer_snippets),
                'results': answer_snippets,
                'raw_response': {'organic_results': results}
            }
        except Exception as e:
            logger.error(f"Поиск в интернете для запроса '{query}' завершился неудачей: {str(e)}")
            return {
                'success': False,
                'results': [],
                'raw_response': {}
            }

    def generate_answer(self, question, conversation_id=None):
        """
        Генерация ответа на заданный вопрос.
        Аргументы:
            question (str): Вопрос пользователя.
            conversation_id (int): ID беседы (опционально).
        Возвращает:
            dict: Словарь с статусом успеха, ответом, источниками, уверенностью и типом источника.
        """
        logger.debug(f"Генерация ответа на вопрос '{question}' в беседе {conversation_id}")
        try:
            # Сначала проверяем базу знаний на наличие похожего вопроса
            knowledge_item = self.nlp_processor.find_similar_question(question)
            if knowledge_item:
                knowledge_item.usage_count += 1
                knowledge_item.last_used = datetime.now()
                knowledge_item.save()
                logger.debug(f"Найден ответ в базе знаний: {knowledge_item.answer}")
                return {
                    'success': True,
                    'answer': knowledge_item.answer,
                    'sources': knowledge_item.sources or [],
                    'confidence': knowledge_item.confidence_score,
                    'source': 'knowledge_base'
                }

            # Если ответа в базе знаний нет, выполняем поиск в интернете
            search_result = self.search_internet(question)
            if not search_result['success']:
                logger.warning(f"Нет результатов поиска для вопроса '{question}'")
                # Предоставление более конкретного ответа для неконкретных запросов
                if question.lower() in ["что нового?", "что нового"]:
                    return {
                        'success': True,
                        'answer': "Пожалуйста, уточните, что именно вы хотите узнать о новостях. Например, новости в Москве или новости технологий?",
                        'sources': [],
                        'confidence': 0.0,
                        'source': 'no_answer'
                    }
                return {
                    'success': True,
                    'answer': f"Не удалось найти информацию по запросу '{question}'. Попробуйте уточнить.",
                    'sources': [],
                    'confidence': 0.0,
                    'source': 'no_answer'
                }

            # Обработка результатов поиска, если они есть
            if search_result['results']:
                answer = "\n".join(f"- {result['title']}: {result['text']}" for result in search_result['results'][:3])
                sources = [{'url': result['source'], 'text': result['title']} for result in search_result['results'][:3]]
                if conversation_id:
                    self.learning_module.update_knowledge_base(
                        question=question,
                        answer=answer,
                        sources=sources,
                        confidence=0.8
                    )
                logger.debug(f"Сгенерирован ответ из поиска: {answer}")
                return {
                    'success': True,
                    'answer': answer,
                    'sources': sources,
                    'confidence': 0.8,
                    'source': 'internet_search'
                }

            # Резервный вариант, если результаты не найдены
            return {
                'success': True,
                'answer': f"Не удалось найти информацию по запросу '{question}'. Попробуйте уточнить.",
                'sources': [],
                'confidence': 0.0,
                'source': 'no_answer'
            }
        except Exception as e:
            logger.error(f"Генерация ответа для вопроса '{question}' завершилась неудачей: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'answer': "Произошла ошибка при обработке вашего вопроса.",
                'sources': [],
                'confidence': 0.0
            }

    def process_message(self, message_text, user, conversation_id=None):
        """
        Обработка сообщения пользователя и генерация ответа.
        Аргументы:
            message_text (str): Сообщение пользователя.
            user: Объект пользователя.
            conversation_id (int): ID беседы (опционально).
        Возвращает:
            dict: Словарь с статусом успеха, ответом, источниками и уверенностью.
        """
        logger.debug(f"Обработка сообщения '{message_text}' для пользователя {user.id}, беседа {conversation_id}")
        try:
            # Валидация сообщения
            if not message_text or not isinstance(message_text, str):
                raise ValueError("Неверный формат сообщения")

            message_text = message_text.strip()
            if len(message_text) < 2:
                raise ValueError("Сообщение слишком короткое")

            # Сначала пробуем обработчик ответа
            handler_response = self.response_handler.process_input(message_text, conversation_id, user)
            if handler_response.get('success'):
                logger.debug(f"Ответ от ResponseHandler: {handler_response['answer']}")
                return handler_response

            # Если обработчик ответа не сработал, генерируем ответ с помощью модели ИИ
            ai_response = self.generate_answer(message_text, conversation_id)
            if not ai_response.get('success'):
                raise ValueError(ai_response.get('error', 'Ошибка генерации ответа'))

            return {
                'success': True,
                'answer': ai_response.get('answer', ''),
                'sources': ai_response.get('sources', []),
                'confidence': ai_response.get('confidence', 0.0)
            }
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения '{message_text}': {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'answer': "Извините, произошла ошибка. Пожалуйста, попробуйте позже.",
                'sources': []
            }