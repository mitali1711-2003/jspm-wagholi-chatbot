<!-- cspell:ignore Wagholi JSPM langdetect gunicorn Gunicorn NLTK mindmate kaggle Kaggle SPPU Procfile bcrypt NAAC AICTE JSCOE RSCOE ICOER JSIMR jspm MiniLM HuggingFace MHT chatbots difflib webkitSpeechRecognition embeddings cosine SequenceMatcher -->
<!-- cspell:ignore प्रवेश कैसे आवेदन करें प्रवेशासाठी अर्ज करावा राउंड माध्यम फेऱ्यांद्वारे -->

# CampusConnect AI + MindMate AI

## Project Report

**Institution:** JSPM University, Wagholi Campus, Pune

**Domain:** Artificial Intelligence, Natural Language Processing, Web Development

**Platform:** Python / Flask

**Database:** SQLite3

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Objective](#2-objective)
3. [Scope of the Project](#3-scope-of-the-project)
4. [Proposed System](#4-proposed-system)
5. [Technology Stack](#5-technology-stack)
6. [Methodology](#6-methodology)
7. [Security and Ethical Considerations](#7-security-and-ethical-considerations)
8. [Testing and Validation](#8-testing-and-validation)
9. [Future Scope](#9-future-scope)
10. [Conclusion](#10-conclusion)
11. [Project Structure](#11-project-structure)
12. [Database Schema](#12-database-schema)
13. [NLP Engine](#13-nlp-engine)
14. [All Routes and API Endpoints](#14-all-routes-and-api-endpoints)
15. [Environment Variables](#15-environment-variables)
16. [Running Locally](#16-running-locally)
17. [Deployment](#17-deployment)

---

## 1. Introduction

Modern university campuses serve thousands of students who need instant access to information about admissions, courses, fees, hostel facilities, examinations, placements, and campus infrastructure. Traditional channels — notice boards, email, or manually staffed help desks — are slow, unavailable after hours, and cannot scale to the volume of student queries. Simultaneously, student mental health has become a growing concern at academic institutions, with stress, anxiety, and academic pressure going largely unaddressed due to stigma and lack of accessible support.

**CampusConnect AI + MindMate AI** is a full-stack web application built specifically for **JSPM University, Wagholi Campus, Pune** that addresses both problems in a single unified platform. It provides:

- **CampusConnect AI** — a 24/7 intelligent FAQ chatbot that answers campus-related queries using semantic search powered by sentence-transformers, with responses available in English, Hindi, and Marathi.
- **MindMate AI** — an empathetic mental health support chatbot that detects emotional distress, responds with appropriate support, and tracks mood trends over time through a personal dashboard.

The system is built on Python and Flask, uses SQLite as the database, and includes a comprehensive admin panel for managing FAQs, monitoring usage analytics, reviewing security logs, managing the canteen menu and exam timetable, viewing faculty feedback, and editing the interactive campus map. Additional student utility features include an exam countdown timer, lost and found board, anonymous faculty feedback poll, canteen menu widget, and an academic calendar viewer.

---

## 2. Objective

The primary objectives of this project are:

- **Automate campus information delivery** by building an NLP-powered chatbot capable of answering 100+ JSPM Wagholi-specific FAQs across admissions, courses, fees, hostel, placements, library, facilities, transportation, and contact details.

- **Provide mental health support** through MindMate AI, an always-available chatbot that offers empathetic responses across categories including stress, anxiety, depression, loneliness, academic pressure, motivation, sleep, and relationships, with crisis detection as the highest-priority safety feature.

- **Support trilingual communication** in English, Hindi, and Marathi with human-written translations for every FAQ, so that language is never a barrier for students.

- **Enable voice-driven interaction** through browser-native speech recognition, making the platform accessible to students who prefer speaking over typing.

- **Empower administrators** with a comprehensive admin panel providing real-time analytics, conversation monitoring, security logging, FAQ management, canteen menu management, exam timetable management, faculty feedback analytics, and a live campus map editor.

- **Enhance student campus life** through utility tools: an exam countdown timer, lost and found board, anonymous faculty feedback poll, daily canteen menu, and a personal profile with mood trend charts.

- **Ensure security and reliability** through bcrypt-hashed authentication, session-based role access control, rate limiting, login attempt logging, and an offline-resilient NLP architecture that guarantees 100% uptime even without the ML model.

---

## 3. Scope of the Project

### In Scope

- FAQ-based conversational AI for JSPM University Wagholi Campus only — no other campuses
- Mental health support chatbot with mood logging and trend visualization
- Trilingual support: English, Hindi, Marathi
- Voice input through the Web Speech API
- Student utility features: exam countdown, canteen menu, lost and found, faculty feedback, academic calendar, campus map
- Role-based web application with student and admin interfaces
- Admin tools: FAQ CRUD, bulk JSON upload, analytics, conversation monitoring, security logs, canteen management, timetable management, faculty feedback analytics, map marker editor
- Deployment on Railway, Render.com, and Vercel (experimental)

### Out of Scope

- Integration with the official JSPM University ERP or student information system
- Real-time notifications or push alerts
- Video or audio calling features
- AI-generated answers outside the predefined FAQ dataset (no large language model integration)
- Native mobile application (iOS or Android)
- Payment or fee collection functionality
- Automated email or SMS notifications
- Other JSPM campuses beyond Wagholi

---

## 4. Proposed System

### Overview

The proposed system is a web-based dual-chatbot platform accessible via any modern browser. Students log in with a username and password, choose a language, and can interact with either chatbot or use the utility tools from the dashboard. Admins log in to the same application and access a separate admin panel.

### Architecture

The application follows a three-tier architecture:

- **Presentation Layer** — Jinja2-rendered HTML templates served by Flask, with Vanilla JavaScript handling dynamic interactions (chat, voice, maps, charts), CSS3 with custom properties for theming.
- **Application Layer** — Flask handles routing, authentication, session management, rate limiting, and business logic. The NLP engine (`utils/nlp_engine.py`) processes all chat queries.
- **Data Layer** — SQLite3 stores all persistent data in 11 tables. FAQ datasets are loaded from JSON files on startup. The ML model embeddings are held in memory.

### CampusConnect AI Design

The campus chatbot uses a two-stage NLP pipeline:

1. **Primary path (Semantic Search):** Sentence embeddings computed using `all-MiniLM-L6-v2` at startup. At query time, cosine similarity is computed between the user query and all FAQ embeddings. The top match above confidence threshold 0.38 is returned with the answer in the user's selected language.

2. **Fallback path (Keyword Matching):** If the ML model is unavailable (no internet, no GPU, environment constraints), the system falls back to `SequenceMatcher`-based fuzzy matching with word overlap scoring. This ensures the chatbot is always functional.

### MindMate AI Design

MindMate uses a rule-based weighted keyword classifier operating over 10 emotional categories. Crisis keywords are checked first for safety. The matched category drives response selection from a curated template file, and every interaction logs the detected emotion for the user's mood tracker.

### Admin Panel Design

A separate section of the application gated behind the `admin` role. It provides eight tools covering FAQ management, usage analytics, conversation browsing, security monitoring, canteen menu, exam timetable, faculty feedback, and campus map editing.

---

## 5. Technology Stack

| Layer | Technology | Version / Notes |
| --- | --- | --- |
| Backend Language | Python | 3.11.7 |
| Web Framework | Flask | 3.0.0 |
| WSGI Server | Gunicorn | 21.2.0 (production) |
| Database | SQLite3 | WAL mode, 11 tables, auto-seeded |
| ORM / DB Access | sqlite3 stdlib | Row factory, WAL mode, busy timeout |
| NLP Model | sentence-transformers | `all-MiniLM-L6-v2`, 22M parameters, 384-dim |
| ML Framework | PyTorch | >= 2.0.0 |
| Numerical Computing | NumPy | >= 1.24.0, < 2.0.0 |
| NLP Toolkit | NLTK | 3.8.1 |
| Language Detection | langdetect | 1.0.9 |
| Password Hashing | bcrypt | 4.1.2 |
| Rate Limiting | Flask-Limiter | 3.5.0 |
| Voice Input | Web Speech API | Browser-native (Chrome / Edge) |
| Frontend | Vanilla JavaScript + CSS3 | No frontend framework |
| Charts | Chart.js | 4.4 |
| Map | Leaflet.js | 1.9.4 + OpenStreetMap tiles |
| Onboarding Tour | Intro.js | First-login walkthrough |
| Deployment | Railway / Render.com | Primary / Alternative |
| Deployment (exp.) | Vercel | Experimental (SQLite limitations) |

---

## 6. Methodology

### Development Approach

The project followed an **iterative development** methodology — features were built, tested, and refined in short cycles rather than designed all upfront.

### Phase 1 — Dataset and Data Modelling

- Collected and authored 100+ JSPM Wagholi-specific FAQs across categories: about, colleges, courses, admissions, fees, hostel, placements, library, facilities, transportation, exams, contact.
- Human-translated every FAQ into Hindi and Marathi.
- Designed the 11-table SQLite schema covering users, FAQs, chat history, analytics, login logs, reviews, contact messages, lost and found, canteen menu, faculty feedback, mood logs, and timetable.
- Created the `mindmate_responses.json` template file with curated, empathetic responses across 10 emotional categories.

### Phase 2 — NLP Engine Development

- Integrated `sentence-transformers` (`all-MiniLM-L6-v2`) for semantic FAQ search using cosine similarity.
- Tuned the confidence threshold to 0.38 through empirical testing on varied query phrasings.
- Built the keyword fallback system using `SequenceMatcher` + word overlap to guarantee chatbot availability without the ML model.
- Implemented MindMate's weighted keyword classifier with crisis-first priority and 10-category coverage.
- Built live FAQ suggestion search (`search_faq_questions`) using the same semantic pipeline with a lower threshold of 0.18 for broader autocomplete coverage.

### Phase 3 — Backend and API Development

- Built all Flask routes: authentication (login, signup, logout), student pages, admin pages, and all REST API endpoints.
- Implemented bcrypt-based authentication with role-based access control (decorators `login_required` and `admin_required`).
- Integrated Flask-Limiter (30 req/min) on chat endpoints.
- Implemented session timeout (35-minute server-side lifetime, JS-warned at 30 minutes).
- Implemented admin auto-creation from the `ADMIN_PASSWORD` environment variable for cloud deployments.

### Phase 4 — Frontend Development

- Built 20 Jinja2 templates for all pages.
- Implemented dark/light mode with CSS variables and `localStorage` persistence.
- Integrated Leaflet.js for the interactive campus map with 31 categorized markers.
- Built the admin map editor with inline editing, add/delete markers, and live save.
- Integrated Chart.js for analytics dashboards, mood trend charts, and faculty feedback visualizations.
- Added the Intro.js first-login onboarding tour.
- Implemented voice input via the Web Speech API with language-aware recognition locale.

### Phase 5 — Testing and Deployment

- Tested chatbot responses across all 10+ FAQ categories and all 3 languages.
- Tested the keyword fallback by simulating an environment without sentence-transformers.
- Tested the MindMate crisis path with sensitive keyword variations.
- Tested admin CRUD operations and verified that FAQ reload rebuilt embeddings correctly.
- Deployed to Railway with the ML model pre-downloaded at build time.
- Configured Vercel with the `/tmp` filesystem workaround for read-only environments.

---

## 7. Security and Ethical Considerations

### Authentication Security

- All passwords are hashed using **bcrypt** with a per-user random salt via the `bcrypt` library. Plain-text passwords are never stored or logged.
- Session cookies are configured with `HttpOnly=True` (prevents JavaScript access) and `SameSite=Lax` (mitigates CSRF from cross-origin navigations).
- The Flask `SECRET_KEY` is required for production startup. The app raises a `RuntimeError` at startup if the key is missing in a production environment.
- Sessions expire after **35 minutes** of inactivity. The JavaScript session timeout module warns users at 30 minutes and auto-logs them out.

### Rate Limiting

- Chat API endpoints are limited to **30 requests per minute per IP** using Flask-Limiter. Exceeding this returns a 429 error with a retry-after header and a user-friendly message.

### Login Monitoring

- Every login attempt (success or failure) is recorded in the `login_logs` table with the username, IP address, user-agent string, and timestamp.
- The admin security dashboard automatically flags IPs and usernames with 3 or more failed attempts within any 24-hour window.

### Authorization

- All student routes use the `@login_required` decorator. All admin routes use `@admin_required`.
- The Lost and Found resolve endpoint checks ownership — only the post's creator or an admin can mark an item as resolved.
- Admin API endpoints are never accessible to regular `user`-role sessions.

### Data Privacy — MindMate

- MindMate conversations are stored in `chat_history` with the user ID, allowing users to review their history. However, the detected emotional category (not the message text) is what gets stored in `mood_logs`.
- Every MindMate response includes a **disclaimer** reminding students that MindMate is not a licensed therapist and is not a substitute for professional mental health care.
- Crisis responses provide encouragement to seek professional help and include helpline guidance.

### Data Privacy — Faculty Feedback

- The anonymous faculty feedback poll **does not store the user ID**. The `faculty_feedback` table has no foreign key to `users`. Student identity is permanently dissociated from their feedback at insert time.

### Input Validation

- All API endpoints validate required fields before processing. Invalid inputs return 400 responses with descriptive error messages.
- File upload (dataset bulk upload) is restricted to `.json` files only.
- Canteen category is validated against a fixed set (`breakfast`, `lunch`, `snacks`, `dinner`).
- Review ratings are validated as integers between 1 and 5.
- The `post_type` for lost and found is validated as either `lost` or `found` using a `CHECK` constraint in SQLite.

### Ethical Considerations

- **No AI hallucination risk for campus data:** CampusConnect uses a closed dataset of human-written, verified FAQs. It does not generate answers — it retrieves pre-written ones. This ensures accuracy for sensitive topics like fees and admissions.
- **Mental health responsiveness:** MindMate's crisis detection is given the highest priority in the scoring system (score 999, checked before all other categories) to ensure no crisis keyword goes unmatched.
- **Transparency:** The MindMate disclaimer is returned with every response, making the bot's non-professional nature explicit to users.
- **No biometric data:** The system does not collect biometric, location, or personally sensitive data beyond what is necessary for account management and chat functionality.

---

## 8. Testing and Validation

### Chatbot Response Testing

- Verified responses for all 10+ FAQ categories: about, colleges, courses, admissions, fees, hostel, placements, library, facilities, transportation, exams, contact.
- Tested query variations (paraphrasing, misspellings, partial queries) to validate the semantic search robustness.
- Confirmed that queries below the 0.38 confidence threshold return the fallback message and a "Did you mean?" suggestion.
- Tested all three languages (English, Hindi, Marathi) to confirm the correct language answer is returned.

### Fallback Testing

- Simulated an environment without PyTorch/sentence-transformers to confirm the keyword matching fallback activates automatically and returns relevant answers.
- Confirmed the app starts and serves requests with no errors in the offline-model scenario.

### MindMate Testing

- Tested crisis keywords across multiple phrasings to ensure the crisis category is always triggered at highest priority.
- Tested all 10 emotional categories with representative messages to confirm correct classification.
- Verified that mood logs are written to the DB and appear correctly on the profile chart.

### Authentication Testing

- Tested signup with duplicate username and duplicate email — confirmed proper error messages.
- Tested login with wrong password — confirmed failure is logged to `login_logs` and no session is created.
- Tested session expiry by waiting past the timeout — confirmed auto-redirect to login.
- Tested admin-only routes with a regular user session — confirmed 302 redirect to login.
- Tested the Lost and Found resolve endpoint with a non-owner user ID — confirmed 403 response.

### Admin Panel Testing

- Tested FAQ create, update, and delete — confirmed `reload_faqs()` runs and embeddings are rebuilt after each operation.
- Tested bulk JSON upload with a valid dataset file and an invalid non-JSON file — confirmed validation.
- Tested canteen menu add and delete operations and verified the student dashboard reflects today's menu.
- Tested timetable CRUD and verified the exam countdown on the dashboard updates.
- Tested map marker save on local filesystem and confirmed the updated JSON is served on the next map load.

### Rate Limit Testing

- Sent more than 30 requests per minute to `/api/chat/campus` from the same IP — confirmed 429 response with the correct error message and `retry_after` field.

### Security Testing

- Tested the admin security dashboard with simulated failed login attempts — confirmed IPs and usernames appear in the suspicious activity lists after 3 or more failures within 24 hours.

---

## 9. Future Scope

### Short-Term Improvements

- **Persistent database on Vercel:** Replace SQLite with a hosted PostgreSQL database (e.g., Neon via Vercel Marketplace) so that user accounts and data persist across deployments.
- **Email notifications:** Send welcome emails on signup and alert admins when a new contact form message is submitted.
- **Chatbot confidence display:** Show the user a visual confidence indicator alongside responses so they know how certain the bot is.
- **More campus languages:** Add support for additional regional languages spoken by students at JSPM.

### Medium-Term Improvements

- **Large language model integration:** Integrate a small, locally runnable LLM (e.g., Mistral 7B via Ollama) or a cloud API (Claude, GPT-4) to generate dynamic, context-aware answers for queries outside the FAQ dataset, while using the existing semantic search as a primary filter.
- **Real-time notifications:** Push notifications (via WebSockets or Server-Sent Events) for new Lost and Found posts, admin announcements, and exam timetable changes.
- **Student ID integration:** Link accounts to official JSPM student IDs to enable personalized features like branch-specific FAQ filtering and individual timetable views.
- **Multilingual voice output:** Add text-to-speech responses using the Web Speech Synthesis API so the chatbot can read answers aloud in the user's language.
- **Mobile application:** Build a React Native or Flutter app wrapping the existing REST API for a native mobile experience.

### Long-Term Improvements

- **ERP / SIS integration:** Connect to the JSPM University student information system to fetch live data for attendance, results, fee payment status, and course registrations directly into chatbot responses.
- **Multi-campus support:** Extend the platform to all JSPM campuses by adding campus-selection at login and maintaining separate FAQ datasets per campus.
- **AI-powered feedback analysis:** Use sentiment analysis and topic clustering on faculty feedback comments to generate automated insight reports for the admin.
- **Counselor escalation:** Integrate MindMate with a professional counseling ticketing system so that crisis-flagged conversations can be routed to a human counselor with appropriate consent.
- **Offline mobile chatbot:** Package the FAQ dataset and a lightweight keyword model into an offline-capable progressive web app so students can get answers without internet access.

---

## 10. Conclusion

**CampusConnect AI + MindMate AI** successfully delivers a full-stack, production-ready intelligent platform tailored to JSPM University's Wagholi Campus. The system demonstrates that a meaningful AI-powered application can be built without relying on expensive closed-source APIs — the core NLP pipeline uses open-source sentence-transformers running entirely on the server with a robust keyword fallback for zero-dependency environments.

The dual-chatbot architecture cleanly separates two distinct problem domains: precise, verified campus information retrieval (CampusConnect) and empathetic, safety-first mental health support (MindMate). This separation ensures that responses in each domain are appropriate to their context — factual accuracy for campus queries, emotional sensitivity and crisis-first prioritization for mental health interactions.

The trilingual design (English, Hindi, Marathi) with voice input and human-written translations reflects the linguistic reality of Maharashtra's student population and ensures the platform serves all students regardless of language preference.

The admin panel provides campus administrators with full operational control — FAQ management, live analytics, security monitoring, canteen and timetable management, faculty feedback review, and map editing — without requiring any technical knowledge or direct database access.

The project has been deployed on Railway and is structured for straightforward deployment on Render.com and Vercel. The offline-resilient NLP architecture, session security, rate limiting, bcrypt authentication, and anonymous faculty feedback design reflect production engineering standards appropriate for a real campus deployment.

---

## 11. Project Structure

```text
chatbot/
├── app.py                         # All Flask routes, auth decorators, API handlers
├── create_admin.py                # One-shot script to create the admin user
├── requirements.txt               # Python dependencies
├── runtime.txt                    # Python 3.11.7
├── Procfile                       # gunicorn start command for Railway/Render
├── railway.json                   # Railway config (pre-downloads ML model at build)
├── render.yaml                    # Render.com deployment config
├── .env.example                   # Template for required environment variables
│
├── models/
│   └── database.py                # SQLite schema (11 tables), get_db(), init_db(), load_dataset_to_db()
│
├── utils/
│   ├── auth.py                    # hash_password() and check_password() using bcrypt
│   ├── nlp_engine.py              # Semantic search, keyword fallback, language detection, MindMate logic
│   ├── scraper.py                 # 100+ hardcoded JSPM Wagholi FAQs — loaded into DB on every startup
│   └── integrate_kaggle.py        # Kaggle mental health dataset integration utility
│
├── database/
│   ├── jspm_wagholi_dataset.json  # Primary campus FAQ dataset (auto-loaded on startup)
│   ├── mindmate_responses.json    # MindMate response templates by emotional category
│   ├── campus_dataset.json        # Additional campus data
│   ├── campus_markers.json        # Map marker data (editable via admin panel)
│   ├── exam_dates.json            # SPPU exam dates for the dashboard countdown widget
│   ├── kaggle_mental_health_raw.json
│   └── kaggle_temp/intents.json
│
├── templates/                     # 20 Jinja2 HTML templates
│   ├── login.html
│   ├── signup.html                # Registration with password strength meter
│   ├── dashboard.html             # Bot cards, exam countdown, canteen widget, onboarding tour
│   ├── select_language.html       # Language picker (English / Hindi / Marathi)
│   ├── campus_chat.html           # CampusConnect AI chat interface
│   ├── mindmate_chat.html         # MindMate AI chat interface
│   ├── campus_map.html            # Leaflet.js campus map (31 markers)
│   ├── academic_calendar.html     # Embedded PDF viewer for 2025-26 academic calendar
│   ├── contact.html               # Contact form + embedded map
│   ├── lost_found.html            # Lost and Found board
│   ├── feedback_poll.html         # Anonymous faculty feedback poll
│   ├── profile.html               # Profile + Chart.js weekly mood trend + doughnut chart
│   ├── footer_wagholi.html        # Shared footer partial
│   ├── admin.html                 # Admin hub + FAQ management (CRUD + bulk JSON upload)
│   ├── admin_analytics.html       # Analytics dashboard
│   ├── admin_conversations.html   # Conversation browser with per-user activity and reviews
│   ├── admin_security.html        # Login logs + suspicious IP/user detection
│   ├── admin_canteen.html         # Canteen menu editor (by date and meal category)
│   ├── admin_feedback.html        # Aggregated faculty feedback viewer
│   ├── admin_timetable.html       # Exam timetable editor
│   └── admin_map.html             # Campus map marker editor (inline editing, save to JSON)
│
└── static/
    ├── css/style.css              # Unified stylesheet — light/dark themes, all page styles
    ├── js/
    │   ├── chat.js                # Chat UI, voice input, typing indicator, export (.txt), review modal
    │   ├── admin.js               # FAQ CRUD, dataset upload, analytics charts (Chart.js)
    │   ├── theme.js               # Dark/light mode toggle with localStorage persistence
    │   ├── session_timeout.js     # 30-min inactivity warning modal; auto-logout at 35 min
    │   └── map/wagholi_map.js     # Fetches markers from API and renders via Leaflet.js
    ├── images/campus-bg.jpg
    └── docs/academic_calendar_2025_26.pdf
```

---

## 12. Database Schema

SQLite3, auto-created by `init_db()` on every startup.

**Local path:** `database/chatbot.db`

**Vercel path:** `/tmp/chatbot.db` (read-only filesystem outside `/tmp` — data is ephemeral on Vercel)

| Table | Purpose |
| --- | --- |
| `users` | Accounts — username, email, bcrypt hash, role (`user`/`admin`), preferred language |
| `faqs` | Trilingual FAQ entries — EN/HI/MR questions and answers, category, campus, active flag |
| `chat_history` | All conversations — user ID, bot type, messages, language, campus |
| `analytics` | Per-query logs with confidence score and matched FAQ ID |
| `login_logs` | Every login attempt (success or failed) with IP address and user-agent |
| `reviews` | Star ratings (1–5) and written feedback submitted at end of conversation |
| `contact_messages` | Contact form submissions — name, email, phone, subject, message |
| `lost_found` | Student posts — type, item name, description, location, contact, resolved flag |
| `canteen_menu` | Daily menu — date, category (breakfast/lunch/snacks/dinner), item name, price |
| `faculty_feedback` | Anonymous ratings — subject, faculty name, rating (1–5), comment; no user ID |
| `mood_logs` | MindMate emotional category logged per message per user (drives mood chart) |
| `timetable` | Exam schedule — exam name, date, branch, semester, note, active flag |

---

## 13. NLP Engine

### CampusConnect AI — Semantic Search (`utils/nlp_engine.py`)

1. On startup, all active FAQs are loaded from the DB and embedded using `all-MiniLM-L6-v2` (22M parameters, 384-dimensional vectors).
2. Each FAQ is embedded as a combined string of its English + Hindi + Marathi questions.
3. At query time, the user message is encoded into the same embedding space.
4. Cosine similarity is computed against all FAQ embeddings; top-3 candidates are selected.
5. **Confidence threshold is 0.38** — scores below this return a friendly fallback message plus a "Did you mean?" suggestion.
6. Among top-3, the system prefers the candidate whose answer exists in the user's selected language (within 85% of the top score).
7. If PyTorch or sentence-transformers is unavailable, the system falls back to **keyword matching** using `SequenceMatcher` (60% weight) + word overlap (40% weight) with a 0.25 threshold.

The `get_did_you_mean()` function uses Python's `difflib.get_close_matches` (cutoff 0.4) on low-confidence queries to suggest the nearest FAQ question.

The `search_faq_questions()` function powers live-as-you-type FAQ suggestions (debounced at 300ms). The semantic path uses threshold 0.18 for broader autocomplete coverage; the keyword path uses substring match plus sequence similarity.

### MindMate AI — Keyword Category Matching

MindMate uses a rule-based weighted keyword classifier, not ML embeddings.

**Step 1 — Crisis check (always first):** All crisis keywords ("suicide", "self-harm", etc.) are checked before any other scoring. A match immediately assigns score 999 and skips all other categories.

**Step 2 — Category scoring:** For all other categories, each keyword is scored as follows:

- Multi-word phrase match: **+5 points**
- Exact whole-word match (surrounded by spaces): **+3 points**
- Substring match: **+1 point**

The category with the highest total score is selected.

**Categories:** `crisis`, `stress`, `anxiety`, `depression`, `loneliness`, `motivation`, `academic`, `sleep`, `relationships`, `default`

**Step 3 — Response selection:** A response is chosen at random from the matched category's template list in `mindmate_responses.json`. The `{name}` placeholder is replaced with the student's capitalized username.

**Step 4 — Mood logging:** The matched category is written to `mood_logs` so it appears in the user's profile mood trend chart.

---

## 14. All Routes and API Endpoints

### Public Routes

| Method | Route | Description |
| --- | --- | --- |
| GET | `/` | Redirects to dashboard if logged in, else to login |
| GET / POST | `/login` | Login — logs every attempt to `login_logs` |
| GET / POST | `/signup` | Registration — validates uniqueness of username and email |
| GET | `/logout` | Clears session |

### Student Routes (login required)

| Method | Route | Description |
| --- | --- | --- |
| GET | `/dashboard` | Main hub — bot cards, exam countdown, canteen widget, onboarding tour |
| GET | `/select-language` | Language picker before chat; `?bot=campus` or `?bot=mindmate` |
| GET | `/chat/campus` | CampusConnect AI chat interface |
| GET | `/chat/mindmate` | MindMate AI chat interface |
| GET | `/campus-map` | Interactive campus map with 31 categorized markers |
| GET | `/academic-calendar` | PDF viewer for the 2025-26 academic calendar |
| GET | `/contact` | Contact form |
| GET | `/lost-found` | Lost and Found board |
| GET | `/feedback` | Anonymous faculty feedback poll |
| GET | `/profile` | Profile page with chat stats and mood charts |

### Admin Routes (admin role required)

| Route | Description |
| --- | --- |
| `/admin` | Admin hub with quick-access cards + FAQ management |
| `/admin/analytics` | Analytics dashboard — top queries, daily usage, language stats |
| `/admin/conversations` | All chats, most-asked questions, per-user activity, reviews |
| `/admin/security` | Login logs, suspicious IPs (3+ failures in 24h), hourly charts |
| `/admin/canteen` | Canteen menu editor — add/remove items by date and meal category |
| `/admin/feedback` | Aggregated faculty feedback — avg ratings, distribution chart, recent comments |
| `/admin/timetable` | Exam timetable CRUD — entries shown as countdown on the student dashboard |
| `/admin/map` | Map marker editor — inline edit names/descriptions, add/delete markers, save |

### Authenticated API Endpoints

| Method | Route | Description |
| --- | --- | --- |
| POST | `/api/chat/campus` | CampusConnect response; saves to `chat_history` and `analytics` |
| POST | `/api/chat/mindmate` | MindMate response; saves to `chat_history`, `analytics`, `mood_logs` |
| GET | `/api/suggestions` | FAQ suggestions — `?q=` for live search, omit for random |
| GET | `/api/history` | User's chat history — last 50 messages, filtered by `?bot_type=` |
| POST | `/api/review` | Submit star rating (1–5) + optional written feedback |
| POST | `/api/set-language` | Set `en` / `hi` / `mr` in session |
| GET | `/api/campus-markers` | All campus map markers as JSON |
| POST | `/api/contact` | Submit contact form to `contact_messages` |
| POST | `/api/lost-found` | Post a lost or found item |
| POST | `/api/lost-found/<id>/resolve` | Mark item resolved — only owner or admin |
| GET | `/api/canteen/today` | Today's canteen menu grouped by category |
| POST | `/api/feedback` | Submit anonymous faculty feedback — no user ID stored |
| GET | `/api/mood-data` | Last 7-day mood trend + overall distribution for profile chart |

### Admin API Endpoints

| Method | Route | Description |
| --- | --- | --- |
| GET | `/api/admin/faqs` | List all FAQs ordered by category |
| POST | `/api/admin/faqs` | Create FAQ — triggers `reload_faqs()` to rebuild embeddings |
| PUT | `/api/admin/faqs/<id>` | Update FAQ — triggers `reload_faqs()` |
| DELETE | `/api/admin/faqs/<id>` | Delete FAQ — triggers `reload_faqs()` |
| POST | `/api/admin/upload-dataset` | Bulk upload FAQs from a JSON file |
| GET | `/api/admin/analytics` | Top queries, language stats, daily usage (30 days), totals |
| GET | `/api/admin/conversations` | Paginated chats, top-20 questions, per-user activity, reviews, avg ratings |
| GET | `/api/admin/security-logs` | Login logs (last 200), suspicious IPs/users, hourly chart data |
| GET | `/api/admin/canteen` | Canteen menu for a specific date (`?date=YYYY-MM-DD`) |
| POST | `/api/admin/canteen` | Add a menu item |
| DELETE | `/api/admin/canteen/<id>` | Remove a menu item |
| GET | `/api/admin/feedback` | Aggregated ratings by subject/faculty + recent 50 responses |
| POST | `/api/admin/campus-markers` | Save edited marker array to JSON |
| GET | `/api/admin/timetable` | All timetable entries ordered by exam date |
| POST | `/api/admin/timetable` | Create timetable entry |
| PUT | `/api/admin/timetable/<id>` | Update timetable entry |
| DELETE | `/api/admin/timetable/<id>` | Delete timetable entry |

---

## 15. Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `SECRET_KEY` | **Yes** | Flask session encryption key. App raises `RuntimeError` on startup in production without this. |
| `ADMIN_PASSWORD` | Yes (setup) | Used by `create_admin.py`. Auto-creates admin on startup if no admin exists in the DB. |
| `PORT` | No | Auto-set by Railway / Render. Defaults to 5000. |
| `HF_HUB_OFFLINE` | No | Set to `1` to use the cached HuggingFace model and skip all network calls. |
| `TRANSFORMERS_OFFLINE` | No | Set to `1` for the same effect on the transformers library. |
| `VERCEL` | Auto | Set automatically by Vercel. Switches DB and markers path to `/tmp/`. |
| `FLASK_ENV` | No | Set to `production` to enforce `SECRET_KEY` requirement at startup. |

---

## 16. Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set required environment variables
export SECRET_KEY='any-random-string'
export ADMIN_PASSWORD='your-admin-password'

# Create the admin user
python create_admin.py

# Run in development mode
python app.py
# Open http://127.0.0.1:5000

# Or run with gunicorn (production mode)
gunicorn app:app --bind 0.0.0.0:5000 --timeout 120 --workers 2
```

First startup downloads the `all-MiniLM-L6-v2` model (~80 MB). If there is no internet connection, the app falls back to keyword matching automatically.

To skip the HuggingFace network check entirely:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python app.py
```

**Common issues:**

- **App hangs on startup:** Use the `HF_HUB_OFFLINE=1` command above.
- **Port 5000 in use:** Run `lsof -ti:5000 | xargs kill -9`
- **SECRET_KEY error:** Export `SECRET_KEY` before running.
- **Admin login not working:** Run `python create_admin.py` after setting `ADMIN_PASSWORD`.

---

## 17. Deployment

### Railway (Primary)

1. Push code to GitHub.
2. Connect the repo on [railway.app](https://railway.app) — auto-detects `railway.json`.
3. `railway.json` pre-downloads the ML model during the build step, then starts gunicorn with 2 workers and a 120s timeout.
4. Add `SECRET_KEY` in the Railway Variables tab.
5. Generate a public domain under Settings → Networking.

### Render.com (Alternative)

1. Connect repo on the Render dashboard — auto-detects `render.yaml`.
2. `SECRET_KEY` is auto-generated by Render.

### Vercel (Experimental)

- `vercel.json` exists in the repo.
- Vercel's filesystem is read-only outside `/tmp` — the DB and marker edits are lost on each cold start.
- Not recommended for production due to SQLite ephemerality; suitable for demos only.
