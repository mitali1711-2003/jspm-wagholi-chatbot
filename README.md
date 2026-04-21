# JSPM Wagholi Campus Chatbot + MindMate AI

A dual-bot Flask web application providing **campus information** and **mental health support** for students at JSPM University, Wagholi Campus, Pune.

**Live Demo:** *(Add your Railway URL here after deployment)*

---

## Project Description (For Resume)

> **CampusConnect & MindMate AI** — Built a full-stack AI-powered dual-chatbot web application using **Flask, Python, NLP, and SQLite**. The system features two intelligent bots: **CampusConnect AI**, which answers 100+ campus FAQs using semantic search powered by sentence-transformers (all-MiniLM-L6-v2) with cosine similarity matching, and **MindMate AI**, a mental health support bot with crisis detection and weighted keyword classification across 10 emotional categories. Implemented **trilingual support** (English, Hindi, Marathi) with human-written translations, **voice input** via Web Speech API, **bcrypt-based authentication** with role-based access control, and a comprehensive **admin panel** with analytics dashboards, conversation monitoring, and security logging (suspicious IP detection). The NLP pipeline includes a graceful **offline fallback** from ML-based semantic search to keyword matching, ensuring 100% uptime regardless of model availability. Deployed on **Railway** with Gunicorn, handling concurrent users with WAL-mode SQLite.
>
> **Key Technologies:** Python, Flask, SQLite, sentence-transformers (PyTorch), NLP, bcrypt, REST APIs, Jinja2, JavaScript, CSS3, Gunicorn, Railway
>
> **Highlights:**
> - Designed and implemented a semantic search engine with 384-dimensional embeddings and confidence-scored responses
> - Built a mental health bot with priority-based crisis detection and personalized response routing
> - Developed a full admin dashboard with real-time analytics, conversation tracking, and security monitoring
> - Engineered an offline-resilient architecture with automatic ML-to-keyword fallback
> - Supported 3 languages with voice input across all interfaces

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
- [FAQ Categories](#faq-categories)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

### CampusConnect AI (Campus Chatbot)
- Answers **100+ FAQs** about JSPM Wagholi — admissions, fees, hostel, courses, placements, facilities, transportation, exams, and more
- Semantic search powered by **sentence-transformers** (`all-MiniLM-L6-v2`, 22M parameters)
- Confidence-scored responses with smart fallback for unknown queries
- Falls back to **keyword matching** if the ML model is unavailable (offline-safe)

### MindMate AI (Mental Health Bot)
- Supportive conversations across categories: stress, anxiety, loneliness, academic pressure, motivation
- **Crisis detection** with highest-priority response routing
- Personalized responses using the student's name
- Includes a disclaimer that MindMate is not a licensed therapist

### Multilingual (English, Hindi, Marathi)
- Language selection screen before chat
- All FAQs available in **3 languages** with human-written translations
- Auto language detection via `langdetect`
- Voice input respects selected language (`en-IN`, `hi-IN`, `mr-IN`)

### Voice Input
- Speech-to-text using **Web Speech API** (Chrome/Edge)
- Language-aware recognition based on user's selected language

### User System
- Signup / Login with **bcrypt-hashed** passwords
- Session-based authentication with role support (`user` / `admin`)
- Chat history per user (last 50 messages)
- Star rating (1-5) and written feedback after conversations

### Admin Panel
- **FAQ Management** — Create, edit, delete, bulk upload (JSON) trilingual FAQs
- **Analytics** — Top queries, daily usage trends, language distribution, bot type breakdown
- **Conversations** — Browse all chats, most-asked questions, per-user activity, reviews & ratings
- **Security** — Login logs, suspicious IP detection (3+ failed attempts in 24h), hourly login charts

### Other Features
- Dark / Light mode toggle with `localStorage` persistence
- Interactive campus map (Wagholi campus)
- Contact form with database storage
- Fully responsive design (mobile-friendly)
- Review/rating system at end of conversations

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 3.0.0, Gunicorn |
| Database | SQLite3 (WAL mode, auto-seeded from JSON) |
| NLP / ML | sentence-transformers (all-MiniLM-L6-v2), PyTorch, NumPy, NLTK, langdetect |
| Auth | bcrypt (salted password hashing) |
| Voice | SpeechRecognition + Web Speech API |
| Frontend | Vanilla JavaScript, CSS3 (CSS variables for light/dark theming) |
| Deployment | Railway / Render.com (Procfile + gunicorn) |

---

## Project Structure

```
jspm-wagholi-chatbot/
├── app.py                          # Main Flask app — routes, auth, APIs
├── create_admin.py                 # Script to bootstrap admin user
├── requirements.txt                # Python dependencies
├── runtime.txt                     # Python version (3.11.7)
├── Procfile                        # Gunicorn start command
├── railway.json                    # Railway deployment config
├── render.yaml                     # Render.com deployment config
├── README.md                       # This file
│
├── models/
│   └── database.py                 # SQLite schema (7 tables), connection helpers, data loader
│
├── utils/
│   ├── auth.py                     # hash_password() and check_password() using bcrypt
│   ├── nlp_engine.py               # Semantic search, keyword fallback, language detection
│   ├── scraper.py                  # 100+ hardcoded JSPM Wagholi FAQs (authoritative dataset)
│   └── integrate_kaggle.py         # Kaggle mental health dataset integration
│
├── database/
│   ├── jspm_wagholi_dataset.json   # Campus FAQ dataset (auto-loaded on startup)
│   ├── mindmate_responses.json     # MindMate AI response templates by category
│   ├── campus_dataset.json         # Additional campus data
│   └── kaggle_mental_health_raw.json # Raw training data
│
├── templates/                      # 13 Jinja2 HTML templates
│   ├── login.html                  # Login page
│   ├── signup.html                 # Registration page
│   ├── dashboard.html              # Main dashboard with bot selection
│   ├── select_language.html        # Language picker (EN / HI / MR)
│   ├── campus_chat.html            # CampusConnect AI chat interface
│   ├── mindmate_chat.html          # MindMate AI chat interface
│   ├── campus_map.html             # Interactive campus map
│   ├── contact.html                # Contact form
│   ├── footer_wagholi.html         # Shared footer partial
│   ├── admin.html                  # Admin FAQ management
│   ├── admin_analytics.html        # Admin analytics dashboard
│   ├── admin_conversations.html    # Admin conversation browser
│   └── admin_security.html         # Admin security/login logs
│
└── static/
    ├── css/
    │   └── style.css               # Unified stylesheet (light/dark themes, 1500+ lines)
    ├── js/
    │   ├── chat.js                 # Chat UI, voice input, review modal
    │   ├── admin.js                # FAQ CRUD, dataset upload, analytics charts
    │   ├── theme.js                # Dark/light mode toggle
    │   └── map/
    │       └── wagholi_map.js      # Campus map rendering
    └── images/
        └── campus-bg.jpg           # Campus background image
```

---

## Installation

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/mitali1711-2003/jspm-wagholi-chatbot.git
cd jspm-wagholi-chatbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Create admin user (optional)
python create_admin.py
```

> **Note:** First startup downloads the `all-MiniLM-L6-v2` model (~80MB) from HuggingFace. Subsequent starts use the cached model. If there's no internet, the app falls back to keyword-based matching automatically.

---

## Running the App

### Development

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

### Production (Local)

```bash
gunicorn app:app --bind 0.0.0.0:5000 --timeout 120 --workers 2
```

### Create Admin User

```bash
export ADMIN_PASSWORD='your-secure-password'
python create_admin.py
```

---

## Deployment

### Railway (Recommended)

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) and sign in with GitHub
3. Click **New Project** → **Deploy from GitHub Repo** → Select `jspm-wagholi-chatbot`
4. Railway auto-detects `railway.json` and builds the app
5. Go to **Settings → Networking → Generate Domain** to get your public URL
6. Add environment variable in **Variables** tab:
   - `SECRET_KEY` = any random string

The `railway.json` config:
- Pre-downloads the ML model during build
- Uses gunicorn with 2 workers and 120s timeout
- Auto-restarts on failure

### Render.com (Alternative)

1. Push to GitHub
2. Connect repo on [Render Dashboard](https://dashboard.render.com)
3. Render auto-detects `render.yaml` and deploys
4. `SECRET_KEY` is auto-generated

### Environment Variables for Deployment

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** | — | Flask session encryption key (app refuses to start without it) |
| `ADMIN_PASSWORD` | **Yes** (for `create_admin.py`) | — | Password for the admin user |
| `PORT` | Auto | `5000` | Set automatically by Railway/Render |
| `HF_HUB_OFFLINE` | No | `1` | Prevents HuggingFace network calls (uses cached model) |
| `TRANSFORMERS_OFFLINE` | No | `1` | Same as above for transformers library |

### Important Notes on Deployment

- **SQLite is ephemeral** on Railway/Render — the database is re-created and seeded from JSON files on every deploy. User accounts and chat history won't persist across redeploys. This is fine for demos and projects.
- **Large dependencies** — `torch` + `sentence-transformers` are ~2GB. The build step pre-downloads the ML model so it's cached.
- If the ML model fails to load, the app **still works** using keyword-based matching as fallback.

---

## Admin Panel

Access at `/admin` (requires admin role login).

| Section | Path | Description |
|---------|------|-------------|
| FAQ Management | `/admin` | Add, edit, delete FAQs in 3 languages; bulk JSON upload |
| Analytics | `/admin/analytics` | Daily usage charts, top queries, language stats, total users/chats |
| Conversations | `/admin/conversations` | All chats with filters, most-asked questions, per-user activity, reviews |
| Security | `/admin/security` | Login logs, suspicious IPs/users (3+ failures in 24h), hourly login charts |

### FAQ JSON Upload Format

To bulk upload FAQs via the admin panel, use this JSON structure:

```json
{
  "campus": "JSPM University - Wagholi Campus",
  "faqs": [
    {
      "category": "admissions",
      "question_en": "How do I apply for admission?",
      "question_hi": "प्रवेश के लिए कैसे आवेदन करें?",
      "question_mr": "प्रवेशासाठी अर्ज कसा करावा?",
      "answer_en": "Apply through MHT-CET CAP rounds...",
      "answer_hi": "MHT-CET CAP राउंड के माध्यम से आवेदन करें...",
      "answer_mr": "MHT-CET CAP फेऱ्यांद्वारे अर्ज करा..."
    }
  ]
}
```

---

## Database Schema

The app uses **SQLite3** with 7 tables, auto-created on startup:

| Table | Columns | Purpose |
|-------|---------|---------|
| `users` | id, username, email, password_hash, role, preferred_language, created_at | User accounts |
| `faqs` | id, category, question_en/hi/mr, answer_en/hi/mr, campus, is_active, created_at, updated_at | Trilingual FAQ entries |
| `chat_history` | id, user_id, bot_type, user_message, bot_response, language, campus, created_at | All user-bot conversations |
| `analytics` | id, query_text, matched_faq_id, bot_type, language, confidence, user_id, created_at | Query logs with confidence scores |
| `login_logs` | id, username, ip_address, user_agent, status, created_at | Login attempts (success/failed) |
| `reviews` | id, user_id, username, bot_type, rating, feedback, created_at | Star ratings and feedback |
| `contact_messages` | id, name, email, phone, subject, message, created_at | Contact form submissions |

---

## NLP Engine

### Campus Chatbot — Semantic Search

1. On startup, loads all active FAQs from the database
2. Computes **sentence embeddings** for all FAQ questions using `all-MiniLM-L6-v2` (22M parameters)
3. User query is encoded into the same 384-dimensional embedding space
4. **Cosine similarity** finds the top-3 matching FAQs
5. Among top candidates, prefers the one with a non-empty answer in the user's language
6. Responses above confidence threshold (**0.38**) are returned; lower scores get a helpful fallback
7. If sentence-transformers is unavailable, falls back to **keyword matching** using `SequenceMatcher` and word overlap scoring

### MindMate AI — Keyword Category Matching

1. **Crisis detection first** (highest priority) — matches keywords like "suicide", "self-harm", etc.
2. Weighted keyword matching across categories:
   - Multi-word phrases: **5 points** (strong signals)
   - Exact whole-word match: **3 points**
   - Substring match: **1 point**
3. Categories: `crisis`, `stress`, `anxiety`, `depression`, `loneliness`, `motivation`, `academic`, `sleep`, `relationships`, `default`
4. Responses are personalized with `{name}` placeholder replaced by the student's username
5. Always includes a disclaimer that MindMate is not a substitute for professional help

---

## Multilingual Support

| Language | Code | Voice Recognition Locale |
|----------|------|--------------------------|
| English | `en` | `en-IN` |
| Hindi | `hi` | `hi-IN` |
| Marathi | `mr` | `mr-IN` |

- Users select their preferred language on a dedicated screen before entering chat
- Language is stored in the Flask session and can be switched anytime
- All 100+ FAQs have **human-written translations** in all 3 languages
- Auto language detection via `langdetect` library when set to auto mode

---

## API Endpoints

### Public Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Redirects to dashboard or login |
| GET/POST | `/login` | User login page |
| GET/POST | `/signup` | User registration page |
| GET | `/logout` | Clear session and redirect to login |

### Authenticated Routes (Login Required)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/dashboard` | Main dashboard with bot selection |
| GET | `/select-language` | Language selection screen |
| GET | `/chat/campus` | CampusConnect AI chat page |
| GET | `/chat/mindmate` | MindMate AI chat page |
| GET | `/campus-map` | Interactive campus map |
| GET | `/contact` | Contact form page |

### Authenticated API Endpoints

| Method | Route | Request Body | Response |
|--------|-------|-------------|----------|
| POST | `/api/chat/campus` | `{ message, language }` | `{ response, language, confidence, category }` |
| POST | `/api/chat/mindmate` | `{ message }` | `{ response, category, disclaimer }` |
| GET | `/api/suggestions?language=en` | — | `{ suggestions: [...] }` |
| GET | `/api/history?bot_type=campus` | — | `{ history: [...] }` |
| POST | `/api/review` | `{ rating, feedback, bot_type }` | `{ success, message }` |
| POST | `/api/contact` | `{ name, email, phone, subject, message }` | `{ success, message }` |
| POST | `/api/set-language` | `{ language }` | `{ success, language }` |

### Admin API Endpoints (Admin Role Required)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/admin/faqs` | List all FAQs |
| POST | `/api/admin/faqs` | Create a new FAQ |
| PUT | `/api/admin/faqs/<id>` | Update an existing FAQ |
| DELETE | `/api/admin/faqs/<id>` | Delete a FAQ |
| POST | `/api/admin/upload-dataset` | Bulk upload FAQs from JSON file |
| GET | `/api/admin/analytics` | Usage analytics (top queries, daily trends, language stats) |
| GET | `/api/admin/conversations` | Conversation data (chats, top questions, user activity, reviews) |
| GET | `/api/admin/security-logs` | Login logs, suspicious IPs/users, hourly charts |

---

## FAQ Categories

The campus chatbot covers the following categories for JSPM Wagholi:

| Category | Topics Covered |
|----------|---------------|
| **About** | University history, establishment (founded 2000, Wagholi campus 2008, university status 2023), NAAC accreditation |
| **Admissions** | MHT-CET, JEE Main, CAP rounds, management quota, direct admission, eligibility criteria |
| **Courses** | B.E./B.Tech (CSE, IT, ENTC, Mech, Civil), MBA, MCA, B.Pharm, D.Pharm, Diploma programs |
| **Fees** | Tuition fees for all programs, hostel fees, scholarship information |
| **Placements** | Recruiting companies (TCS, Infosys, Wipro, etc.), packages (3-12 LPA), placement cell details |
| **Hostel** | Room types, mess facilities, fees, rules, capacity |
| **Library** | Digital resources, timings, membership, e-journals |
| **Exams** | SPPU exam schedule, internal assessments, grading system |
| **Facilities** | Computer labs, sports complex, WiFi, canteen, auditorium |
| **Transportation** | Bus routes, timings, pick-up/drop-off points |
| **Clubs & Activities** | Technical clubs, cultural events, hackathons, sports tournaments |
| **Contact** | Phone numbers, email addresses, campus address, office hours |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** | — | Flask session encryption key (app refuses to start without it) |
| `ADMIN_PASSWORD` | **Yes** (for `create_admin.py`) | — | Password for the admin user |
| `PORT` | No | `5000` | Server port (auto-set by Railway/Render) |
| `HF_HUB_OFFLINE` | No | `1` | Use cached HuggingFace model (no network calls) |
| `TRANSFORMERS_OFFLINE` | No | `1` | Same as above for transformers library |

---

## Troubleshooting

### App hangs on startup
The sentence-transformers library tries to connect to HuggingFace to check for model updates. If there's no internet, it retries and hangs. **Fix:** Set environment variables:
```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python app.py
```

### "Address already in use" error
Another process is using port 5000 (common on macOS with AirPlay Receiver). **Fix:**
```bash
# Kill the process on port 5000
lsof -ti:5000 | xargs kill -9
# Or use a different port
python app.py  # then change port in app.py
```

### Model download fails
If the `all-MiniLM-L6-v2` model can't be downloaded, the app automatically falls back to keyword-based matching. The chatbot will still work, just with slightly lower accuracy.

### Admin login not working
Run the admin creation script:
```bash
export ADMIN_PASSWORD='your-secure-password'
python create_admin.py
```

### Dependencies fail to install
Make sure you're using Python 3.11+:
```bash
python3 --version
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Authors

Developed for **JSPM University, Wagholi Campus, Pune**.

## License

This project is developed for educational purposes at JSPM University, Wagholi Campus, Pune.

---

## About This Project

This project is a full-stack AI-powered dual-chatbot platform built for JSPM University's Wagholi Campus. It combines **CampusConnect AI** — a semantic search-driven FAQ bot covering admissions, placements, hostel, courses, and more — with **MindMate AI**, a mental health support companion featuring crisis detection and emotionally aware responses. The application supports three languages (English, Hindi, Marathi), voice input, secure authentication, and a comprehensive admin panel with analytics and security monitoring. Designed to run both online and offline, it ensures students always have access to campus information and mental wellness support.
