# CampusConnect AI + MindMate AI

A dual-bot Flask web application providing **campus information** and **mental health support** for students at JSPM University, Wagholi Campus, Pune.

**Live Demo:** *(Add your Railway URL here after deployment)*

---

## Project Description (For Resume)

> **CampusConnect & MindMate AI** — Built a full-stack AI-powered dual-chatbot web application using **Flask, Python, NLP, and SQLite**. The system features two intelligent bots: **CampusConnect AI**, which answers 100+ campus FAQs using semantic search powered by sentence-transformers (all-MiniLM-L6-v2) with cosine similarity matching, and **MindMate AI**, a mental health support bot with crisis detection and weighted keyword classification across 10 emotional categories. Implemented **trilingual support** (English, Hindi, Marathi) with human-written translations, **voice input** via Web Speech API, **bcrypt-based authentication** with role-based access control, and a comprehensive **admin panel** with analytics dashboards, conversation monitoring, security logging, canteen menu management, exam timetable management (with PDF upload), faculty feedback analytics, and an interactive **campus map editor**. Additional student utility features include an SPPU exam countdown widget, academic calendar PDF viewer, Lost & Found board, anonymous faculty feedback polls, and a personal profile page with a MindMate mood tracker (Chart.js). The NLP pipeline includes a graceful **offline fallback** from ML-based semantic search to keyword matching, ensuring 100% uptime regardless of model availability. Deployed on **Railway** with Gunicorn.
>
> **Key Technologies:** Python, Flask, SQLite, sentence-transformers (PyTorch), NLP, bcrypt, REST APIs, Jinja2, Vanilla JavaScript, CSS3, Chart.js, Leaflet.js, Gunicorn, Railway
>
> **Highlights:**
> - Designed and implemented a semantic search engine with 384-dimensional embeddings and confidence-scored responses
> - Built a mental health bot with priority-based crisis detection, mood logging, and weekly mood trend charts
> - Developed a full admin dashboard with real-time analytics, conversation tracking, security monitoring, canteen management, exam timetable with PDF upload, feedback analytics, and a live map marker editor
> - Engineered student utility tools: exam countdown timer, academic calendar PDF viewer, Lost & Found board, canteen menu widget, anonymous faculty feedback poll
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
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Features

### CampusConnect AI (Campus Chatbot)
- Answers **100+ FAQs** about JSPM Wagholi — admissions, fees, hostel, courses, placements, facilities, transportation, exams, and more
- Semantic search powered by **sentence-transformers** (`all-MiniLM-L6-v2`, 22M parameters)
- Confidence-scored responses with smart fallback for unknown queries
- Falls back to **keyword matching** if the ML model is unavailable (offline-safe)
- Live FAQ suggestions while typing (debounced dropdown, 300ms)

### MindMate AI (Mental Health Bot)
- Supportive conversations across categories: stress, anxiety, loneliness, academic pressure, motivation, sleep, relationships
- **Crisis detection** with highest-priority response routing
- Personalized responses using the student's name
- **Mood logging** — every MindMate message logs the detected emotional category
- Includes a disclaimer that MindMate is not a licensed therapist

### Student Utility Tools
- **Exam Countdown Widget** — Live countdown to the next SPPU exam on the dashboard, loaded from `exam_dates.json`
- **Canteen Menu of the Day** — Today's menu displayed on the dashboard; admins update it via the admin panel
- **Academic Calendar** — Full 2025–26 JSPM academic calendar as an embedded PDF viewer (holidays, exam schedules, key dates)
- **Lost & Found Board** — Students post lost/found items; filter by type; mark as resolved
- **Anonymous Faculty Feedback Poll** — Rate any subject/faculty (1–5 stars) with optional comments; identity never stored
- **My Profile Page** — Displays account info, chat stats, and a Chart.js weekly mood trend chart + distribution doughnut from MindMate sessions

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
- Creative animated info panel on login/signup pages showcasing all platform features
- Session-based authentication with role support (`user` / `admin`)
- **Session timeout warning modal** — warns at 30 min, auto-logs out at 35 min; resets on any user action
- Chat history per user (last 50 messages)
- Star rating (1–5) and written feedback after conversations
- **First-login onboarding tour** powered by Intro.js, highlighting key features

### Campus Map
- Interactive **Leaflet.js** map of JSPM Wagholi campus
- 31 categorised markers: Academic, Admin, Library, Sports, Hostels, PGs, Food, Transport
- Accurate GPS coordinates (corrected to GAT No. 720, JSPM Road)
- Markers loaded dynamically from `campus_markers.json` via API

### Admin Panel
- **Admin Hub** — Dashboard with quick-access cards to all admin tools
- **FAQ Management** — Create, edit, delete, bulk upload (JSON) trilingual FAQs
- **Analytics** — Top queries, daily usage trends, language distribution, bot type breakdown
- **Conversations** — Browse all chats, most-asked questions, per-user activity, reviews & ratings
- **Security** — Login logs, suspicious IP detection (3+ failed attempts in 24h), hourly login charts
- **Canteen Menu Editor** — Add/remove menu items per meal category per date; students see today's menu on the dashboard
- **Exam Timetable Editor** — Full CRUD for exam schedule entries; upload a timetable PDF that students can view
- **Faculty Feedback Viewer** — Aggregated ratings by subject/faculty, rating distribution chart, recent comments
- **Map Editor** — Edit building names and descriptions inline, add/delete markers, save to JSON; changes reflect on the live map instantly

### UI / UX
- Dark / Light mode toggle with `localStorage` persistence
- Typing indicator ("bot is typing…") with CSS animation in both chat interfaces
- Chat export — download conversation as `.txt` file (JS Blob, no backend)
- Responsive design (mobile-friendly)
- Sticky save bar with unsaved-change count in the map editor

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 3.0.0, Flask-Limiter, Gunicorn |
| Database | SQLite3 (WAL mode, auto-seeded from JSON) |
| NLP / ML | sentence-transformers (all-MiniLM-L6-v2), PyTorch, NumPy, NLTK, langdetect |
| Auth | bcrypt (salted password hashing) |
| Voice | Web Speech API (browser-native) |
| Frontend | Vanilla JavaScript, CSS3 (CSS variables for light/dark theming) |
| Charts | Chart.js 4.4 (analytics, mood tracker, feedback) |
| Map | Leaflet.js 1.9.4 + OpenStreetMap tiles |
| Tour | Intro.js (first-login onboarding) |
| Rate Limiting | Flask-Limiter (30 req/min on chat endpoints) |
| Deployment | Railway / Render.com (Procfile + gunicorn) |

---

## Project Structure

```
CampusConnect-AI/
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
│   └── database.py                 # SQLite schema (12 tables), connection helpers, data loader
│
├── utils/
│   ├── auth.py                     # hash_password() and check_password() using bcrypt
│   ├── nlp_engine.py               # Semantic search, keyword fallback, language detection
│   ├── scraper.py                  # 100+ JSPM Wagholi FAQs (authoritative dataset)
│   └── integrate_kaggle.py         # Kaggle mental health dataset integration
│
├── database/
│   ├── jspm_wagholi_dataset.json   # Campus FAQ dataset (auto-loaded on startup)
│   ├── mindmate_responses.json     # MindMate AI response templates by category
│   ├── campus_dataset.json         # Additional campus data
│   ├── campus_markers.json         # Map marker data (editable via admin panel)
│   ├── exam_dates.json             # SPPU exam dates for countdown widget
│   └── kaggle_mental_health_raw.json
│
├── templates/                      # 21 Jinja2 HTML templates
│   ├── login.html                  # Login page with animated feature info panel
│   ├── signup.html                 # Registration (password strength meter + info panel)
│   ├── dashboard.html              # Main dashboard — bot cards, exam countdown, canteen widget, onboarding tour
│   ├── select_language.html        # Language picker (EN / HI / MR)
│   ├── campus_chat.html            # CampusConnect AI chat interface
│   ├── mindmate_chat.html          # MindMate AI chat interface
│   ├── campus_map.html             # Interactive Leaflet.js campus map
│   ├── academic_calendar.html      # Embedded PDF viewer for 2025–26 academic calendar
│   ├── contact.html                # Contact form + embedded map
│   ├── lost_found.html             # Lost & Found board
│   ├── feedback_poll.html          # Anonymous faculty feedback poll
│   ├── profile.html                # User profile + mood trend charts
│   ├── footer_wagholi.html         # Shared footer partial
│   ├── admin.html                  # Admin hub + FAQ management
│   ├── admin_analytics.html        # Admin analytics dashboard
│   ├── admin_conversations.html    # Admin conversation browser
│   ├── admin_security.html         # Admin security/login logs
│   ├── admin_canteen.html          # Admin canteen menu editor
│   ├── admin_timetable.html        # Admin exam timetable editor + PDF upload
│   ├── admin_feedback.html         # Admin faculty feedback viewer
│   └── admin_map.html              # Admin campus map marker editor
│
└── static/
    ├── css/
    │   └── style.css               # Unified stylesheet (light/dark themes, admin tool cards)
    ├── js/
    │   ├── chat.js                 # Chat UI, voice input, typing indicator, chat export, review modal
    │   ├── admin.js                # FAQ CRUD, dataset upload, analytics charts
    │   ├── theme.js                # Dark/light mode toggle
    │   ├── session_timeout.js      # 30-min inactivity warning modal
    │   └── map/
    │       └── wagholi_map.js      # Campus map — fetches markers from API, renders Leaflet
    ├── images/
    │   └── campus-bg.jpg
    └── docs/
        ├── academic_calendar_2025_26.pdf   # Embedded academic calendar
        └── timetable.pdf                   # Admin-uploaded exam timetable (auto-created)
```

---

## Installation

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/mitali1711-2003/CampusConnect-AI.git
cd CampusConnect-AI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Create admin user
export ADMIN_PASSWORD='your-secure-password'
python create_admin.py
```

> **Note:** First startup downloads the `all-MiniLM-L6-v2` model (~80MB) from HuggingFace. Subsequent starts use the cached model. If there's no internet, the app falls back to keyword-based matching automatically.

---

## Running the App

### Development

```bash
export SECRET_KEY='your-random-secret-key'
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

### Production (Local)

```bash
SECRET_KEY='your-random-secret-key' gunicorn app:app --bind 0.0.0.0:5000 --timeout 120 --workers 2
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
3. Click **New Project** → **Deploy from GitHub Repo** → Select `CampusConnect-AI`
4. Railway auto-detects `railway.json` and builds the app
5. Go to **Settings → Networking → Generate Domain** to get your public URL
6. Add environment variables in the **Variables** tab:
   - `SECRET_KEY` = any random string

The `railway.json` config pre-downloads the ML model during build, uses gunicorn with 2 workers and 120s timeout.

### Render.com (Alternative)

1. Push to GitHub
2. Connect repo on [Render Dashboard](https://dashboard.render.com)
3. Render auto-detects `render.yaml` and deploys
4. `SECRET_KEY` is auto-generated

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** | — | Flask session encryption key (app refuses to start without it) |
| `ADMIN_PASSWORD` | **Yes** (for `create_admin.py`) | — | Password for the admin user |
| `PORT` | Auto | `5000` | Set automatically by Railway/Render |
| `HF_HUB_OFFLINE` | No | `1` | Prevents HuggingFace network calls (uses cached model) |
| `TRANSFORMERS_OFFLINE` | No | `1` | Same as above for transformers library |
| `VERCEL` | Auto | — | Set by Vercel; switches DB and uploads to `/tmp/` |

> **Note:** SQLite is ephemeral on Railway/Render — the database is re-created and seeded from JSON on every deploy. User accounts won't persist across redeploys. Fine for demos.

---

## Admin Panel

Access at `/admin` (requires admin role). The admin hub shows quick-access cards for all tools.

| Section | Path | Description |
|---------|------|-------------|
| FAQ Management | `/admin` | Add, edit, delete FAQs in 3 languages; bulk JSON upload |
| Analytics | `/admin/analytics` | Daily usage charts, top queries, language stats, total users/chats |
| Conversations | `/admin/conversations` | All chats with filters, most-asked questions, per-user activity, reviews |
| Security | `/admin/security` | Login logs, suspicious IPs/users (3+ failures in 24h), hourly login charts |
| Canteen Menu | `/admin/canteen` | Add/remove menu items per category (breakfast/lunch/snacks/dinner) per date |
| Exam Timetable | `/admin/timetable` | Add/edit/delete exam schedule entries; upload timetable PDF for students |
| Faculty Feedback | `/admin/feedback` | Aggregated ratings by subject & faculty, rating distribution chart, recent comments |
| Map Editor | `/admin/map` | Edit building names/descriptions inline, add/delete markers, save to `campus_markers.json` |

### Timetable PDF Upload

In the timetable admin page, a **PDF Upload** card lets admins:
- Upload a PDF timetable (replaces any previously uploaded file)
- Preview the live PDF in a new tab
- Remove the PDF if needed

Students can view the uploaded PDF at `/timetable-pdf` (login required).

### FAQ JSON Upload Format

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

The app uses **SQLite3** with 12 tables, auto-created on startup:

| Table | Purpose |
|-------|---------|
| `users` | User accounts (username, email, bcrypt hash, role, language preference) |
| `faqs` | Trilingual FAQ entries (EN/HI/MR questions and answers, category, active flag) |
| `chat_history` | All user-bot conversations with bot type, language, and campus |
| `analytics` | Query logs with confidence scores and matched FAQ IDs |
| `login_logs` | Login attempts (success/failed) with IP and user-agent |
| `reviews` | Star ratings and written feedback per conversation |
| `contact_messages` | Contact form submissions |
| `lost_found` | Student lost/found item posts (type, item, description, location, contact, resolved flag) |
| `canteen_menu` | Daily canteen menu items (date, category, item name, price) |
| `faculty_feedback` | Anonymous faculty ratings (subject, faculty name, rating 1–5, comment) |
| `mood_logs` | MindMate emotional category logs per user per message (for profile chart) |
| `timetable` | Exam schedule entries (exam name, date, branch, semester, note, active flag) |

---

## NLP Engine

### Campus Chatbot — Semantic Search

1. On startup, loads all active FAQs from the database
2. Computes **sentence embeddings** for all FAQ questions using `all-MiniLM-L6-v2` (22M parameters, 384-dim)
3. User query is encoded into the same embedding space
4. **Cosine similarity** finds the top-3 matching FAQs
5. Prefers the candidate with a non-empty answer in the user's selected language
6. Responses above confidence threshold (**0.38**) are returned; lower scores trigger a helpful fallback
7. If sentence-transformers is unavailable, falls back to **keyword matching** using `SequenceMatcher` + word overlap scoring

### MindMate AI — Keyword Category Matching

1. **Crisis detection first** (highest priority) — keywords like "suicide", "self-harm", etc.
2. Weighted keyword matching across categories:
   - Multi-word phrases: **5 points**
   - Exact whole-word match: **3 points**
   - Substring match: **1 point**
3. Categories: `crisis`, `stress`, `anxiety`, `depression`, `loneliness`, `motivation`, `academic`, `sleep`, `relationships`, `default`
4. Detected category is **logged to `mood_logs`** for the profile mood chart
5. Responses personalized with student's username

---

## Multilingual Support

| Language | Code | Voice Recognition Locale |
|----------|------|--------------------------|
| English | `en` | `en-IN` |
| Hindi | `hi` | `hi-IN` |
| Marathi | `mr` | `mr-IN` |

All 100+ FAQs have human-written translations in all 3 languages. Auto language detection via `langdetect`.

---

## API Endpoints

### Public Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Redirects to dashboard or login |
| GET/POST | `/login` | User login |
| GET/POST | `/signup` | User registration |
| GET | `/logout` | Clear session |

### Authenticated Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/dashboard` | Main dashboard |
| GET | `/select-language` | Language selection |
| GET | `/chat/campus` | CampusConnect AI chat |
| GET | `/chat/mindmate` | MindMate AI chat |
| GET | `/campus-map` | Interactive campus map |
| GET | `/academic-calendar` | Embedded academic calendar PDF viewer |
| GET | `/timetable-pdf` | View admin-uploaded exam timetable PDF |
| GET | `/contact` | Contact form |
| GET | `/lost-found` | Lost & Found board |
| GET | `/feedback` | Anonymous faculty feedback form |
| GET | `/profile` | User profile + mood charts |

### Authenticated API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/chat/campus` | Campus bot response |
| POST | `/api/chat/mindmate` | MindMate bot response |
| GET | `/api/suggestions` | FAQ autocomplete suggestions |
| GET | `/api/history` | User chat history |
| POST | `/api/review` | Submit star rating |
| POST | `/api/contact` | Submit contact form |
| POST | `/api/set-language` | Set session language |
| POST | `/api/lost-found` | Post a lost/found item |
| POST | `/api/lost-found/<id>/resolve` | Mark item as resolved |
| GET | `/api/canteen/today` | Today's canteen menu |
| POST | `/api/feedback` | Submit anonymous faculty feedback |
| GET | `/api/mood-data` | Weekly mood data for profile chart |
| GET | `/api/campus-markers` | All campus map markers (JSON) |

### Admin API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/admin/faqs` | List all FAQs |
| POST | `/api/admin/faqs` | Create FAQ |
| PUT | `/api/admin/faqs/<id>` | Update FAQ |
| DELETE | `/api/admin/faqs/<id>` | Delete FAQ |
| POST | `/api/admin/upload-dataset` | Bulk upload FAQs |
| GET | `/api/admin/analytics` | Usage analytics |
| GET | `/api/admin/conversations` | Conversation data |
| GET | `/api/admin/security-logs` | Security logs |
| GET | `/api/admin/canteen` | Get canteen menu by date |
| POST | `/api/admin/canteen` | Add menu item |
| DELETE | `/api/admin/canteen/<id>` | Remove menu item |
| GET | `/api/admin/timetable` | List all timetable entries |
| POST | `/api/admin/timetable` | Create timetable entry |
| PUT | `/api/admin/timetable/<id>` | Update timetable entry |
| DELETE | `/api/admin/timetable/<id>` | Delete timetable entry |
| GET | `/api/admin/timetable/pdf-status` | Check if timetable PDF is uploaded |
| POST | `/api/admin/timetable/upload-pdf` | Upload timetable PDF |
| DELETE | `/api/admin/timetable/delete-pdf` | Remove timetable PDF |
| GET | `/api/admin/feedback` | Aggregated faculty feedback |
| POST | `/api/admin/campus-markers` | Save edited map markers |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** | — | Flask session encryption key |
| `ADMIN_PASSWORD` | **Yes** (setup) | — | Admin user password |
| `PORT` | No | `5000` | Auto-set by Railway/Render |
| `HF_HUB_OFFLINE` | No | `1` | Use cached HuggingFace model |
| `TRANSFORMERS_OFFLINE` | No | `1` | Same for transformers |
| `VERCEL` | Auto | — | Switches DB and file uploads to `/tmp/` |

---

## Troubleshooting

### App hangs on startup
Set offline flags to skip HuggingFace network checks:
```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python app.py
```

### "Address already in use" on port 5000
```bash
lsof -ti:5000 | xargs kill -9
```

### SECRET_KEY error on startup
The app refuses to start without `SECRET_KEY`. Export it before running:
```bash
export SECRET_KEY='any-random-string-here'
python app.py
```

### Model download fails
The app automatically falls back to keyword-based matching. The chatbot will still work.

### Admin login not working
```bash
export ADMIN_PASSWORD='your-secure-password'
python create_admin.py
```

---

## About This Project

Full-stack AI-powered dual-chatbot platform for JSPM University's Wagholi Campus combining **CampusConnect AI** (semantic FAQ search) with **MindMate AI** (mental health support with mood tracking). Features trilingual support, voice input, an exam countdown, academic calendar viewer, canteen menu, lost & found board, anonymous faculty feedback, a profile page with mood charts, and a comprehensive admin panel with exam timetable management (including PDF upload) and a live map editor. Built with Python, Flask, SQLite, sentence-transformers, Chart.js, and Leaflet.js.

---

*Developed for educational purposes at JSPM University, Wagholi Campus, Pune.*
