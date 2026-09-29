# RoboMatch — Платформа подбора роботизированных решений

## Описание

**RoboMatch** — веб-платформа для экспресс-предынвестиционной оценки целесообразности роботизации. Сервис помогает компаниям подобрать роботизированные решения под конкретный объект (склад, аэропорт, медицинское учреждение), сравнить альтернативы, рассчитать экономический эффект и визуализировать работу роботов.

### Целевая аудитория
- Руководители предприятий и функциональных подразделений
- Технические директора, руководители по автоматизации
- Логисты, операционные и финансовые аналитики
- Специалисты, готовящие предварительное обоснование проектов роботизации

### Ключевые функции
- **Каталог решений** — 15+ роботизированных решений с характеристиками (AMR, FMR, роботы-штабелеры, тягачи, уборщики, беспилотные погрузчики, системы кубического хранения)
- **Подбор и рекомендации** — автоматический подбор подходящих роботов на основе параметров объекта с объяснением причин
- **Экономический расчёт** — CAPEX, OPEX, годовой эффект, срок окупаемости, ROI, TCO
- **Сравнение сценариев** — базовый, покупка, аренда (RaaS) с графиками и what-if анализом
- **2D-визуализация** — имитация работы роботов на схеме объекта с KPI
- **Экспорт** — PDF-отчёт и Excel-таблицы
- **Роли** — гость, пользователь, администратор

---

## Стек

| Компонент | Технология |
|-----------|-----------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS 3, Chart.js, Lucide Icons |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy ORM, Pydantic |
| **База данных** | SQLite 3 |
| **Аутентификация** | JWT (python-jose, passlib bcrypt) |
| **Экспорт** | ReportLab (PDF), openpyxl (Excel) |
| **Контейнеризация** | Docker, Docker Compose |

---

## Запуск проекта

**Предварительные требования:** Docker и Docker Compose

```bash
cd robomatch

docker-compose up --build

Frontend: http://localhost:3000
Backend API: http://localhost:8000/api/docs
```

### Локальный запуск

**Предварительные требования:** Python 3.11+, Node.js 18+, SQLite 3+

```bash
psql -U postgres
CREATE DATABASE robopodbor;
CREATE USER robopodbor WITH PASSWORD 'robopodbor';
GRANT ALL PRIVILEGES ON DATABASE robopodbor TO robopodbor;
\q
```

```bash
cd backend

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
cd frontend

npm install

npm run dev
```

- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/api/docs

---

## Демонстрационные аккаунты

| Роль | Email | Пароль |
|------|-------|--------|
| Администратор | admin@robopodbor.ru | admin123 |
| Пользователь | demo@robopodbor.ru | demo123 |

При первом запуске БД автоматически заполняется:
- 2 пользователя (админ + демо)
- 3 типа объектов (склад, аэропорт, мед. учреждение)
- 7 категорий роботов
- 15+ решений с характеристиками
- Демо-проект со сценариями

---

## Архитектура

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Frontend  │────▶│   Backend API   │────▶│  PostgreSQL   │
│  React/TS   │◀────│   FastAPI       │◀────│   Database    │
│  port 3000  │     │   port 8000     │     │   port 5432   │
└─────────────┘     └─────────────────┘     └──────────────┘
      │                     │
      │              ┌──────┴──────┐
      │              │  Services   │
      │              ├─────────────┤
      │              │ Economics   │ - расчёт CAPEX/OPEX/ROI/TCO
      │              │ Recommend.  │ - подбор решений
      │              │ Simulation  │ - данные визуализации
      │              └─────────────┘
```

### Структура API

| Группа | Эндпоинт | Описание |
|--------|----------|----------|
| Auth | `POST /api/auth/register` | Регистрация |
| Auth | `POST /api/auth/login` | Вход |
| Auth | `GET /api/auth/me` | Текущий пользователь |
| Objects | `GET /api/objects/` | Типы объектов |
| Objects | `GET /api/objects/{slug}/demo-data` | Демо-данные |
| Catalog | `GET /api/catalog/categories` | Категории роботов |
| Catalog | `GET /api/catalog/solutions` | Каталог (фильтры, поиск, сортировка) |
| Catalog | `POST/PUT/DELETE /api/catalog/solutions` | CRUD (админ) |
| Projects | `GET/POST /api/projects/` | Проекты пользователя |
| Projects | `POST /api/projects/{id}/upload-params` | Загрузка из Excel/CSV |
| Scenarios | `POST /api/projects/{id}/scenarios` | Создание сценария |
| Scenarios | `POST /api/scenarios/{id}/calculate` | Расчёт экономики |
| Scenarios | `GET /api/projects/{id}/compare` | Сравнение сценариев |
| Recommend. | `POST /api/recommendations/match` | Подбор решений |
| Export | `GET /api/projects/{id}/export/pdf` | PDF-отчёт |
| Export | `GET /api/projects/{id}/export/excel` | Excel-отчёт |
| Simulation | `GET /api/projects/{id}/simulation` | Данные визуализации |

---

## Экономическая модель

### Формулы (согласно ТЗ)

| Показатель | Формула |
|-----------|---------|
| **Кол-во роботов** | ⌈Пиковые_операции / (Производительность × 0.85 × 0.95)⌉ × 1.1 |
| **CAPEX** | (N × Цена_ед.) + ПО + Внедрение + Инфраструктура + Обучение + Резерв_10% |
| **OPEX** | Обслуживание + Энергия + Связь + Расходники + Персонал_эксп. + Лицензии |
| **Годовой эффект** | ФОТ_сокращение + Доп_экономия − OPEX_роботизации |
| **Окупаемость** | CAPEX / Годовой_эффект |
| **ROI** | (Эффект_год × T) / CAPEX × 100% |
| **TCO** | CAPEX + Σ(OPEX_i) + Замена_компонентов |

### Допущения
- Коэффициент загрузки робота: 85%
- Доступность робота: 95%
- Резерв по количеству: 10%
- Сокращение персонала по умолчанию: 40%
- Горизонт расчёта: 5 лет

---

## Пользовательский путь

1. **Выбор объекта** → Склад / Аэропорт / Мед. учреждение
2. **Ввод параметров** → вручную или загрузка из файла / демо-данные
3. **Подбор решений** → автоматический с объяснением причин
4. **Сравнение** → по техническим и экономическим характеристикам
5. **Расчёт экономики** → CAPEX, OPEX, ROI, TCO
6. **What-if анализ** → сравнение сценариев (базовый, покупка, RaaS)
7. **Визуализация** → 2D-схема работы роботов с KPI
8. **Экспорт** → PDF-отчёт, Excel-таблицы

---

## Структура проекта

```
robomatch/
├── docker-compose.yml          # Конфигурация Docker
├── README.md                   # Документация
│
├── backend/                    # Python FastAPI Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   └── app/
│       ├── main.py             # Точка входа FastAPI
│       ├── config.py           # Настройки
│       ├── database.py         # Подключение к БД
│       ├── models.py           # SQLAlchemy модели
│       ├── schemas.py          # Pydantic схемы
│       ├── auth.py             # JWT аутентификация
│       ├── seed_data.py        # Начальные данные
│       ├── routers/            # API эндпоинты
│       │   ├── auth.py
│       │   ├── objects.py
│       │   ├── catalog.py
│       │   ├── projects.py
│       │   ├── scenarios.py
│       │   ├── recommendations.py
│       │   ├── export.py
│       │   └── simulation.py
│       └── services/           # Бизнес-логика
│           ├── economics.py    # Экономические расчёты
│           ├── recommendations.py  # Подбор решений
│           └── simulation.py   # Генерация визуализации
│
└── frontend/                   # React TypeScript Frontend
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        ├── api/                # API клиент
        │   ├── client.ts
        │   └── index.ts
        ├── contexts/
        │   └── AuthContext.tsx
        ├── components/
        │   └── Layout.tsx
        └── pages/
            ├── Landing.tsx     # Главная страница
            ├── Login.tsx       # Вход
            ├── Register.tsx    # Регистрация
            ├── Catalog.tsx     # Каталог решений
            ├── CatalogDetail.tsx # Детали решения
            ├── Projects.tsx    # Список проектов
            ├── NewProject.tsx  # Мастер создания проекта
            ├── ProjectDetail.tsx # Проект (сценарии, сравнение, визуализация, экспорт)
            └── Admin.tsx       # Панель администратора
```

---
