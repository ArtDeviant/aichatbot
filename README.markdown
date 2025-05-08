# AI Chatbot with Web Search Integration

## Overview

This project is an AI-powered chatbot built with Python and Django, designed to interact with users through a web interface. The chatbot processes user messages, classifies them, and provides responses by leveraging natural language processing (NLP) and web search capabilities. It integrates with Google and Yandex search engines to fetch relevant information for user queries, processes the results using NLP techniques (BERT and TF-IDF), and stores responses in a knowledge base for improved future interactions.

The chatbot supports multilingual text processing (with a focus on Russian) and includes features like message history, conversation management, and a responsive front-end interface. It is intended for users who need quick answers to various queries, enhanced by real-time web search.

## Features

- **Conversational Interface**: Users can interact with the chatbot through a clean and responsive web interface.
- **NLP Processing**: Utilizes BERT (`bert-base-multilingual-cased`) and TF-IDF for text processing and similarity matching.
- **Web Search Integration**: Fetches results from Google and Yandex using web scraping techniques.
- **Knowledge Base**: Stores responses in a Django-managed database to improve answer retrieval over time.
- **Multilingual Support**: Processes queries in multiple languages, with a focus on Russian (via `spaCy` and BERT).
- **Real-time Messaging**: Displays user and AI messages with timestamps and optional sources for web-sourced answers.
- **Responsive Design**: Built with Bootstrap for a mobile-friendly experience.

## Tech Stack

- **Backend**: Python 3.9+, Django 4.2+
- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript
- **NLP Libraries**:
  - `transformers` (Hugging Face) for BERT model integration
  - `scikit-learn` for TF-IDF vectorization
  - `spacy` with `ru_core_news_sm` for Russian text processing
- **Web Scraping**: `requests` and `beautifulsoup4` for fetching and parsing search results
- **Database**: SQLite (default for Django, can be swapped to PostgreSQL or others)
- **Dependencies**: Managed via `requirements.txt`

## Project Structure

```
ai-chatbot/
│
├── aichat/                    # Main Django app
│   ├── migrations/            # Database migrations
│   ├── static/                # Static files (CSS, JS)
│   ├── templates/aichat/      # HTML templates
│   │   ├── base.html          # Base template with shared layout
│   │   ├── chat.html          # Chat interface template
│   │   └── conversations.html # Conversations list template
│   ├── __init__.py
│   ├── admin.py               # Django admin configuration
│   ├── apps.py                # App configuration
│   ├── models.py              # Database models (Conversation, Message, KnowledgeBase)
│   ├── nlp_processor.py       # NLP processing logic (BERT, TF-IDF, text preprocessing)
│   ├── response_handler.py    # Handles response generation and classification
│   ├── model_manager.py       # Manages AI model interactions
│   ├── utils.py               # Web search and scraping utilities
│   └── views.py               # Django views for handling requests
│
├── chatbot/                   # Django project settings
│   ├── __init__.py
│   ├── settings.py            # Project settings
│   ├── urls.py                # URL routing
│   └── wsgi.py                # WSGI entry point
│
├── manage.py                  # Django management script
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Installation

### Prerequisites

- Python 3.9 or higher
- `pip` (Python package manager)
- Virtual environment (recommended)

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ai-chatbot.git
   cd ai-chatbot
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install spaCy model for Russian**:
   ```bash
   python -m spacy download ru_core_news_sm
   ```

5. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   Open your browser and navigate to `http://127.0.0.1:8000`.

## Usage

1. **Start a Conversation**:
   - Navigate to the homepage (`/`).
   - Click "New Chat" to start a new conversation.
   - Enter a message (e.g., "где кот") and press Enter or click "Send".

2. **View Conversations**:
   - Go to `/conversations/` to see a list of all conversations.
   - Click on a conversation to view its message history.

3. **Interact with the Chatbot**:
   - The chatbot processes your message, classifies it (e.g., as a question or action), and responds.
   - If the answer requires web search, it fetches results from Google and Yandex and displays them with sources.

## Example

**User Input**: "где кот"  
**Chatbot Response**:  
```
- [Source Title 1] (https://example.com)
  Snippet: A brief description about where to find a cat...
- [Source Title 2] (https://example.ru)
  Snippet: Another description related to the query...
```

If no results are found:  
```
- Нет результатов: Не удалось найти информацию по запросу "где кот". Попробуйте уточнить запрос.
```

## Contributing

We welcome contributions! To contribute:

1. **Fork the repository** and clone it locally.
2. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and test them thoroughly.
4. **Commit your changes**:
   ```bash
   git commit -m "Add your feature description"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a pull request** on GitHub.

### Development Notes

- **Testing**: Add unit tests in `aichat/tests.py` using Django's testing framework.
- **Linting**: Use `flake8` to ensure code style consistency.
- **Dependencies**: Update `requirements.txt` if you add new packages.
- **Web Scraping**: Be cautious with search engine scraping; consider adding delays or using APIs to avoid blocks.

## Known Issues

- **Web Scraping**: The current implementation relies on HTML scraping, which may break if Google or Yandex change their page structure. Future improvements may include using official search APIs.
- **Performance**: Loading BERT models can be slow on startup. Consider optimizing or using lighter models for production.
- **Error Handling**: Some edge cases (e.g., network failures) may need better handling.

## Future Improvements

- Replace web scraping with official search APIs (e.g., Google Custom Search API).
- Add support for more languages and improve NLP accuracy.
- Implement caching for frequently asked questions to reduce response time.
- Add user authentication and personalized conversation history.

## Support the Project

If you find this project useful and would like to support its development, consider making a donation via UnionPay:  
💸 6263 0156 0027 6866  

Your support helps keep the project alive and funds future improvements!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, feel free to open an issue on GitHub or contact the maintainers at `da@modesign.site`.
