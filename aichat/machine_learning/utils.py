import logging
import random
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# Инициализация логгера для отслеживания процесса и ошибок
logger = logging.getLogger(__name__)

def search_internet(query, use_selenium=False):
    """
    Выполняет поиск в Google и Яндексе, парсит результаты и возвращает список с заголовками, выдержками и ссылками.
    Аргументы:
        query (str): Поисковый запрос.
        use_selenium (bool): Флаг для использования Selenium (по умолчанию False, так как требует настройки).
    Возвращает:
        list: Список словарей с ключами 'title', 'snippet', 'link' или дефолтный результат при отсутствии данных.
    """
    logger.debug(f"Начало выполнения функции search_internet для запроса: {query}")

    # Список User-Agent'ов для ротации, чтобы избежать блокировок
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    ]
    headers = {"User-Agent": random.choice(user_agents)}
    logger.debug(f"Выбранный User-Agent: {headers['User-Agent']}")

    results = []

    # Функция парсинга результатов Google с обновленными селекторами
    def parse_google(soup):
        """
        Парсит результаты поиска Google на основе структуры HTML из скриншота.
        Аргументы:
            soup (BeautifulSoup): Разобранный HTML страницы Google.
        Возвращает:
            list: Список словарей с результатами поиска.
        """
        try:
            logger.debug("Начало парсинга результатов Google")
            # Основной контейнер результатов на основе скриншота
            for result in soup.select('div#rso div.g'):
                # Извлечение заголовка из тега h3 внутри ссылки
                title_elem = result.select_one('h3.LC20lb')
                if not title_elem:
                    title_elem = result.select_one('h3')  # Резервный вариант
                # Извлечение ссылки из тега a
                link_elem = result.select_one('a[href]')
                # Извлечение выдержки
                snippet_elem = result.select_one('div.VwiC3b.YwPh0e') or result.select_one('div[data-snippet]')

                # Проверка наличия всех необходимых элементов
                if title_elem and link_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem['href'].replace("/url?q=", "").split("&")[0]  # Удаление параметров
                    snippet = snippet_elem.get_text(strip=True)

                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'link': link
                    })
                    logger.debug(f"Найден результат Google: {title} ({link})")
                else:
                    logger.warning("Не удалось извлечь все элементы из результата Google")
            logger.debug(f"Google: найдено {len(results)} результатов")
            return results
        except Exception as e:
            logger.error(f"Ошибка парсинга результатов Google: {str(e)}")
            return []

    # Функция парсинга результатов Яндекса с обновленными селекторами
    def parse_yandex(soup):
        """
        Парсит результаты поиска Яндекса на основе структуры HTML из скриншота.
        Аргументы:
            soup (BeautifulSoup): Разобранный HTML страницы Яндекса.
        Возвращает:
            list: Список словарей с результатами поиска.
        """
        try:
            logger.debug("Начало парсинга результатов Яндекса")
            # Основной контейнер результатов
            for result in soup.select('li.serp-item'):
                # Извлечение заголовка
                title_elem = result.select_one('a.organic__url b') or result.select_one('div.organic__title')
                if not title_elem:
                    title_elem = result.select_one('a.Link')
                # Извлечение ссылки
                link_elem = result.select_one('a.organic__url[href]') or result.select_one('a.Link[href]')
                # Извлечение выдержки
                snippet_elem = result.select_one('div.organic__text')

                if title_elem and link_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem['href']
                    snippet = snippet_elem.get_text(strip=True)

                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'link': link
                    })
                    logger.debug(f"Найден результат Яндекса: {title} ({link})")
                else:
                    logger.warning("Не удалось извлечь все элементы из результата Яндекса")
            logger.debug(f"Яндекс: найдено {len(results)} результатов")
            return results
        except Exception as e:
            logger.error(f"Ошибка парсинга результатов Яндекса: {str(e)}")
            return []

    # Выполнение поиска в Google
    try:
        google_url = f"https://www.google.com/search?q={quote(query)}"
        logger.debug(f"Выполняется поиск в Google по URL: {google_url}")
        response = requests.get(google_url, headers=headers, timeout=15)
        response.raise_for_status()  # Проверка на успешный ответ
        logger.debug(f"Статус ответа Google: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')
        google_results = parse_google(soup)
        results.extend(google_results)
    except requests.exceptions.RequestException as e:
        logger.error(f"Поиск в Google для запроса '{query}' завершился неудачей: {str(e)}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка в поиске Google для запроса '{query}': {str(e)}")

    # Добавление случайной задержки для имитации человеческого поведения
    delay = random.uniform(3, 10)
    logger.debug(f"Задержка перед поиском в Яндексе: {delay} секунд")
    time.sleep(delay)

    # Выполнение поиска в Яндексе
    try:
        yandex_url = f"https://yandex.ru/search/?text={quote(query)}"
        logger.debug(f"Выполняется поиск в Яндексе по URL: {yandex_url}")
        response = requests.get(yandex_url, headers=headers, timeout=15)
        response.raise_for_status()
        logger.debug(f"Статус ответа Яндекса: {response.status_code}")
        soup = BeautifulSoup(response.text, 'html.parser')
        yandex_results = parse_yandex(soup)
        results.extend(yandex_results)
    except requests.exceptions.RequestException as e:
        logger.error(f"Поиск в Яндексе для запроса '{query}' завершился неудачей: {str(e)}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка в поиске Яндекса для запроса '{query}': {str(e)}")

    # Если результатов нет, возвращаем дефолтный ответ
    if not results:
        logger.warning(f"Результатов поиска не найдено для запроса: {query}")
        return [{
            'title': 'Нет результатов',
            'snippet': f'Не удалось найти информацию по запросу "{query}". Попробуйте уточнить запрос.',
            'link': ''
        }]

    # Ограничение количества результатов до 10
    logger.debug(f"Всего возвращено {len(results)} результатов")
    return results[:10]