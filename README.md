# JSPM Wagholi Campus Chatbot + MindMate AI

A dual-bot Flask web application providing **campus information** and **mental health support** for students at JSPM University, Wagholi Campus, Pune.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Deployment](#deployment)
- [Admin Panel](#admin-panel)
- [Database Schema](#database-schema)
- [NLP Engine](#nlp-engine)
- [Multilingual Support](#multilingual-support)
- [API Endpoints](#api-endpoints)
- [Screenshots](#screenshots)
- [License](#license)

---

## Features

### Campus Chatbot
- Answers 100+ FAQs about JSPM Wagholi — admissions, fees, hostel, courses, placements, facilities, transportation, exams, and more
- Semantic search powered by **sentence-transformers** (all-MiniLM-L6-v2)
- Confidence-scored responses with smart fallback for unknown queries

### MindMate AI (Mental Health Bot)
- Supportive conversations across categories: stress, anxiety, loneliness, academic pressure, motivation
- Crisis detection with highest-priority response routing
- Personalized responses using the student's name

### Multilingual (English, Hindi, Marathi)
- Language selection screen before chat
- All FAQs available in 3 languages
- Auto language detection via `langdetect`
- Voice input respects selected language (en-IN, hi-IN, mr-IN)

### Voice Input
- Speech-to-text using Web Speech API (Chrome/Edge)
- Language-aware recognition

### User System
- Signup / Login with bcrypt-hashed passwords
- Session-based authentication with role support (user / admin)
- Chat history per user (last 50 messages)
- Star rating (1-5) and feedback after conversations

### Admin Panel
- **FAQ Management** — Create, edit, delete, bulk upload (JSON) trilingual FAQs
- **Analytics** — Top queries, daily usage trends, language distribution, bot type breakdown
- **Conversations** — Browse all chats, most-asked questions, per-user activity, reviews
- **Security** — Login logs, suspicious IP detection (3+ failed attempts in 24h), hourly charts

### Other
- Dark / Light mode toggle with localStorage persistence
- Interactive campus map
- Contact form
- Responsive design (mobile-friendly)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask 3.0.0, Gunicorn |
| Database | SQLite3 (WAL mode) |
| NLP | sentence-transformers, PyTorch, NLTK, langdetect |
| Auth | bcrypt (salted hashing) |
| Voice | SpeechRecognition + Web Speech API |
| Frontend | Vanilla JS, CSS3 (CSS variables for theming) |
| Deployment | Render.com |

---

## Project Structure

```
chatbot/
├── app.py                      # Main Flask app (routes, auth, API)
├── create_admin.py             # Bootstrap admin user script
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python 3.11.7
├── Procfile                    # Gunicorn config
├── render.yaml                 # Render deployment config
│
├── models/
│   └── database.py             # SQLite schema, connection, data loading
│
├── utils/
│   ├── auth.py                 # Password hashing & verification
│   ├── nlp_engine.py           # Semantic search, language detection, response logic
│   ├── scraper.py              # Hardcoded JSPM Wagholi FAQ dataset (100+ entries)
│   └── integrate_kaggle.py     # Kaggle dataset integration
│
├── database/
│   ├── chatbot.db              # SQLite database
│   ├── jspm_wagholi_dataset.json
│   └── mindmate_responses.json
│
├── templates/                  # 15 Jinja2 HTML templates
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── select_language.html
│   ├── campus_chat.html
│   ├── mindmate_chat.html
│   ├── campus_map.html
│   ├── contact.html
│   ├── admin.html
│   ├── admin_analytics.html
│   ├── admin_conversations.html
│   └── admin_security.html
│
└── static/
    ├── css/style.css           # Unified theme (light/dark, 1500+ lines)
    ├── js/
    │   ├── chat.js             # Chat UI logic, voice input, reviews
    │   ├── admin.js            # FAQ CRUD, dataset upload
    │   └── theme.js            # Dark mode toggle
    └── images/
        └── campus-bg.jpg
```

---

## Installation

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/jspm-wagholi-chatbot.git
cd jspm-wagholi-chatbot

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Create admin user
python create_admin.py
```

> **Note:** First startup will download the `all-MiniLM-L6-v2` model (~80MB). Subsequent starts use the cached model.

---

## Running the App

```bash
# Development
python app.py

# Production
gunicorn app:app --bind 0.0.0.0:5000 --timeout 120
```

Open **http://127.0.0.1:5000** in your browser.

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

---

## Deployment

### Render.com (Preconfigured)

1. Push to GitHub
2. Connect repo on [Render Dashboard](https://dashboard.render.com)
3. Render auto-detects `render.yaml` and deploys

```yaml
# render.yaml
services:
  - type: web
    name: jspm-wagholi-chatbot
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: "3.11"
```

---

## Admin Panel

Access at `/admin` (requires admin role).

| Section | Path | Description |
|---------|------|-------------|
| FAQ Management | `/admin` | Add, edit, delete FAQs in 3 languages; bulk JSON upload |
| Analytics | `/admin/analytics` | Daily usage, top queries, language stats |
| Conversations | `/admin/conversations` | All chats, most-asked questions, user activity, reviews |
| Security | `/admin/security` | Login logs, suspicious IPs/users (3+ failures in 24h) |

---

## Database Schema

| Table | Purpose |
|-------|---------|
| `users` | User accounts (username, email, password_hash, role, preferred_language) |
| `faqs` | Trilingual FAQ entries (question + answer in EN/HI/MR, category, active status) |
| `chat_history` | All user-bot conversations (message, response, bot_type, language) |
| `analytics` | Query logs with confidence scores and matched FAQ IDs |
| `login_logs` | Login attempts with IP, user-agent, success/failure status |
| `reviews` | Star ratings (1-5) and feedback per bot |
| `contact_messages` | Contact form submissions |

---

## NLP Engine

### Campus Chatbot
1. On startup, computes embeddings for all FAQ questions using **all-MiniLM-L6-v2** (22M parameters)
2. User query is encoded into the same embedding space
3. Cosine similarity finds the top-3 matching FAQs
4. Responses above the confidence threshold (0.38) are returned in the user's selected language
5. Low-confidence queries get a helpful fallback message

### MindMate AI
1. Keyword-based category matching with multi-word phrase weighting
2. Categories: `crisis` (highest priority), `stress`, `anxiety`, `loneliness`, `motivation`, `academic`, `default`
3. Responses are personalized with the student's name
4. Includes a disclaimer that MindMate is not a licensed therapist

---

## Multilingual Support

| Language | Code | Voice Recognition |
|----------|------|-------------------|
| English | `en` | `en-IN` |
| Hindi | `hi` | `hi-IN` |
| Marathi | `mr` | `mr-IN` |

- Users select language before entering chat
- Language stored in session and switchable mid-conversation
- All 100+ FAQs have human-written translations in all 3 languages

---

## API Endpoints

### Public
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/login` | User login |
| POST | `/signup` | User registration |

### Authenticated (User)
| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/chat/campus` | Send message to campus chatbot |
| POST | `/api/chat/mindmate` | Send message to MindMate AI |
| GET | `/api/suggestions` | Get random FAQ suggestions |
| GET | `/api/history` | Get user's chat history (last 50) |
| POST | `/api/review` | Submit star rating + feedback |
| POST | `/api/contact` | Submit contact form |
| POST | `/api/set-language` | Set preferred language |

### Admin Only
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/admin/faqs` | List all FAQs |
| POST | `/api/admin/faqs` | Create FAQ |
| PUT | `/api/admin/faqs/<id>` | Update FAQ |
| DELETE | `/api/admin/faqs/<id>` | Delete FAQ |
| POST | `/api/admin/upload-dataset` | Bulk upload FAQs (JSON) |
| GET | `/api/admin/analytics` | Usage analytics data |
| GET | `/api/admin/conversations` | Conversation insights |
| GET | `/api/admin/security-logs` | Login logs & suspicious activity |

---

## FAQ Categories

The chatbot covers the following categories for JSPM Wagholi Campus:

- **About** — University history, establishment (founded 2000, Wagholi campus 2008, university status 2023)
- **Admissions** — MHT-CET, JEE, CAP rounds, management quota
- **Courses** — B.E., B.Tech, MBA, MCA, B.Pharm, D.Pharm, Diploma
- **Fees** — Tuition fees for all programs, hostel fees
- **Placement** — Companies, packages, placement cell
- **Hostel** — Room types, mess, fees, facilities
- **Library** — Digital resources, timings
- **Exams** — SPPU schedule, internal assessments
- **Facilities** — Labs, sports, WiFi, canteen
- **Transportation** — Bus routes, timings
- **Clubs & Activities** — Technical clubs, cultural events
- **Contact** — Phone, email, address

---

## License

This project is developed for JSPM University, Wagholi Campus, Pune.
