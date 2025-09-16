# 📦 AI Replies

Сервис автоматизации работы с отзывами на **Wildberries**:
1. Подгружает свежие отзывы (без ответа).
2. Генерирует ответы с помощью **Google Gemini API**.
3. Публикует их обратно на WB.
4. Работает в режиме **ACID-транзакций** и с **идемпотентностью**.

---

## 🚀 Возможности

- **Fetcher** → получает новые отзывы из WB API и сохраняет в БД.
- **Replier** → генерирует ответы на новые отзывы (статус `draft`).
- **Publisher** → публикует ответы в WB и помечает их как `published`.
- **Pipeline** → объединяет всё в один цикл: Fetch → Reply → Publish.
- **ACID** → каждая операция выполняется в транзакции (всё или ничего).
- **Idempotency** → исключает дублирование по `wb_id`.
- **Логирование** → свой логгер (`logging`) с форматтером.
- **Тесты** → unit-тесты на `pytest` с фейковыми клиентами.
- **Pre-commit хуки** → `ruff`, `mypy`, автоформат.

---

## 🛠️ Технологии

- Python **3.13**
- SQLAlchemy 2.0
- Alembic (миграции)
- Pytest
- Pre-commit (ruff + mypy + автоформат)
- Google GenAI SDK (`google-genai`)
- Wildberries Feedbacks API

---

## 📂 Структура проекта

```bash
ai_replies/
├── app/
│ ├── alembic/
│ ├── clients/
│ ├── core/
│ ├── └────models/
│ ├── services/
│ ├── utils/
│ └── main.py
├── tests/
│ ├── conftest.py
│ ├── test_fetcher.py
│ ├── test_replier.py
│ ├── test_publisher.py
│ └── test_pipeline.py
├── alembic/
├── pyproject.toml
├── .pre-commit-config.yaml
└── README.md
...
```

---

## ⚙️ Установка

1. Установите Python 3.13 и [uv](https://docs.astral.sh/uv/).
2. Склонируйте проект:

```bash
git clone https://github.com/<you>/ai_replies.git
cd ai_replies
```

## Установите зависимости:

```bash
uv sync
```

## Настройте переменные окружения .env по приемру из .env.template

```bash
APP__DB__USER=
APP__DB__PASSWORD=
APP__DB__HOST=0.0.0.0
APP__DB__PORT=5432
APP__DB__DB_NAME=
APP__DB__POOL_PRE_PING=True

APP__API_KEYS__WB_TOKEN=
APP__API_KEYS__GEMINI_TOKEN
```


## Миграции

```bash
uv run alembic upgrade head
```

## Запуск пайплайна

```bash
uv run python app/main.py
```

---

## 🧪 Тестирование

```bash
uv run pytest -v
```

## Проверка стиля и статического анализа:

```bash
uv run pre-commit run -a
uv run mypy app
```

---

## 🛠 Технологии

- **Python 3.13**
- **SQLAlchemy + Alembic**
- **PostgreSQL / SQLite**
- **Google Gemini (google-genai)**
- **Wildberries Feedbacks API**
- **pytest**
- **ruff + mypy + pre-commit**

---

## 📜 Пример лога

```bash
[2025-09-16 12:01:03,456] INFO  - Fetching new reviews from WB
[2025-09-16 12:01:04,120] INFO  - Inserted new review: 123456
[2025-09-16 12:01:04,125] INFO  - Generating replies for new reviews
[2025-09-16 12:01:05,001] INFO  - Generated reply for review 123456
[2025-09-16 12:01:05,220] INFO  - Published reply for review 123456
```

## 📄 Лицензия:  MIT License. Используй свободно.
