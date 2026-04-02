"""
NLP Engine — handles language detection, semantic search, and response generation.
Uses sentence-transformers for similarity matching and langdetect for language detection.
Falls back to keyword matching if sentence-transformers is unavailable.
CONFIGURED FOR JSPM WAGHOLI CAMPUS ONLY.
"""

import json
import os
import re
import random
from difflib import SequenceMatcher
from langdetect import detect

# ─── Offline-safe imports ────────────────────────────────────────
# Force offline mode so sentence-transformers uses cached model
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')

_USE_SEMANTIC = False
_model = None
_np = None
_st_util = None

try:
    import numpy as np
    _np = np
    from sentence_transformers import SentenceTransformer, util as st_util
    _st_util = st_util
    _USE_SEMANTIC = True
except Exception:
    print("[INFO] sentence-transformers not available — using keyword matching fallback")

# ─── Global state ────────────────────────────────────────────────
_faq_embeddings = None
_faq_data = None
_mindmate_data = None


def get_model():
    """Lazy-load the sentence transformer model."""
    global _model, _USE_SEMANTIC
    if not _USE_SEMANTIC:
        return None
    if _model is None:
        try:
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"[WARN] Could not load sentence-transformers model: {e}")
            _USE_SEMANTIC = False
            return None
    return _model


def detect_language(text):
    """Detect language of input text. Returns 'en', 'hi', or 'mr'."""
    try:
        lang = detect(text)
        if lang == 'hi':
            return 'hi'
        elif lang == 'mr':
            return 'mr'
        else:
            return 'en'
    except Exception:
        return 'en'


def load_faqs_from_db():
    """Load Wagholi-only FAQs from database and compute embeddings."""
    global _faq_embeddings, _faq_data
    from models.database import get_db

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faqs WHERE is_active = 1")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return

    _faq_data = [dict(row) for row in rows]

    # Build embeddings if semantic search is available
    model = get_model()
    if model is not None:
        questions = []
        for faq in _faq_data:
            combined = f"{faq['question_en']} {faq.get('question_hi', '')} {faq.get('question_mr', '')}"
            questions.append(combined)
        try:
            _faq_embeddings = model.encode(questions, convert_to_tensor=True)
        except Exception as e:
            print(f"[WARN] Embedding computation failed: {e}")
            _faq_embeddings = None


def _keyword_match(user_message, language='en'):
    """Fallback keyword-based FAQ matching when semantic search is unavailable."""
    if not _faq_data:
        return None, 0.0

    message_lower = user_message.lower().strip()
    message_words = set(re.sub(r'[^\w\s]', ' ', message_lower).split())

    best_faq = None
    best_score = 0.0

    for faq in _faq_data:
        # Check all language variants
        questions = [
            faq.get('question_en', '').lower(),
            faq.get('question_hi', '').lower(),
            faq.get('question_mr', '').lower(),
        ]

        faq_score = 0.0
        for q in questions:
            if not q:
                continue
            # Sequence similarity
            seq_score = SequenceMatcher(None, message_lower, q).ratio()
            # Word overlap
            q_words = set(re.sub(r'[^\w\s]', ' ', q).split())
            if q_words:
                overlap = len(message_words & q_words) / max(len(message_words), 1)
            else:
                overlap = 0.0
            # Combined score
            combined = (seq_score * 0.6) + (overlap * 0.4)
            faq_score = max(faq_score, combined)

        if faq_score > best_score:
            best_score = faq_score
            best_faq = faq

    return best_faq, best_score


def get_campus_response(user_message, language='en', campus='JSPM Wagholi'):
    """
    Find the best FAQ match for a JSPM Wagholi campus query.
    Uses semantic search if available, falls back to keyword matching.
    """
    global _faq_embeddings, _faq_data

    if _faq_data is None or (_USE_SEMANTIC and _faq_embeddings is None):
        load_faqs_from_db()

    if _faq_data is None or len(_faq_data) == 0:
        return {
            'answer': _wagholi_fallback(language),
            'confidence': 0.0,
            'faq_id': None,
            'category': 'unknown'
        }

    # ── Semantic search path ──
    if _USE_SEMANTIC and _faq_embeddings is not None:
        model = get_model()
        if model is not None:
            try:
                query_embedding = model.encode(user_message, convert_to_tensor=True)
                scores = _st_util.cos_sim(query_embedding, _faq_embeddings)[0]

                top_k = min(3, len(_faq_data))
                top_indices = scores.argsort(descending=True)[:top_k]

                best_idx = int(top_indices[0])
                best_score = float(scores[best_idx])

                if best_score < 0.38:
                    return {
                        'answer': _wagholi_fallback(language),
                        'confidence': best_score,
                        'faq_id': None,
                        'category': 'unknown'
                    }

                chosen_idx = best_idx
                for idx in top_indices:
                    idx = int(idx)
                    faq = _faq_data[idx]
                    answer_key = f'answer_{language}'
                    if faq.get(answer_key) and float(scores[idx]) > best_score * 0.85:
                        chosen_idx = idx
                        break

                faq = _faq_data[chosen_idx]
                answer = faq.get(f'answer_{language}') or faq.get('answer_en', '')
                return {
                    'answer': answer,
                    'confidence': float(scores[chosen_idx]),
                    'faq_id': faq.get('id'),
                    'category': faq.get('category', 'general')
                }
            except Exception as e:
                print(f"[WARN] Semantic search failed, using keyword fallback: {e}")

    # ── Keyword fallback path ──
    best_faq, best_score = _keyword_match(user_message, language)

    if best_faq is None or best_score < 0.25:
        return {
            'answer': _wagholi_fallback(language),
            'confidence': best_score,
            'faq_id': None,
            'category': 'unknown'
        }

    answer = best_faq.get(f'answer_{language}') or best_faq.get('answer_en', '')
    return {
        'answer': answer,
        'confidence': best_score,
        'faq_id': best_faq.get('id'),
        'category': best_faq.get('category', 'general')
    }


def _wagholi_fallback(language):
    """Wagholi-specific fallback for unknown queries."""
    fallbacks = {
        'en': "I'm sorry, I don't have that information for JSPM Wagholi Campus. I can help with admissions, courses, fees, hostel, placements, library, facilities, exams, transportation, and contact details — all for JSPM Wagholi only. Try asking about one of these topics!",
        'hi': "क्षमा करें, मेरे पास JSPM वाघोली कैंपस के लिए यह जानकारी नहीं है। मैं प्रवेश, पाठ्यक्रम, शुल्क, छात्रावास, प्लेसमेंट, पुस्तकालय, सुविधाएं, परीक्षा, परिवहन और संपर्क विवरण में मदद कर सकता हूं — केवल JSPM वाघोली के लिए। इनमें से किसी विषय के बारे में पूछें!",
        'mr': "क्षमस्व, माझ्याकडे JSPM वाघोली कॅम्पससाठी ही माहिती नाही. मी प्रवेश, अभ्यासक्रम, शुल्क, वसतिगृह, प्लेसमेंट, ग्रंथालय, सुविधा, परीक्षा, वाहतूक आणि संपर्क तपशील — फक्त JSPM वाघोलीसाठी मदत करू शकतो. यापैकी एखाद्या विषयाबद्दल विचारा!"
    }
    return fallbacks.get(language, fallbacks['en'])


def get_mindmate_response(user_message, language='en', username='friend'):
    """
    Generate empathetic MindMate AI response.
    Personalizes responses with the user's name.
    """
    global _mindmate_data

    mindmate_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'database', 'mindmate_responses.json'
    )
    with open(mindmate_path, 'r', encoding='utf-8') as f:
        _mindmate_data = json.load(f)

    categories = _mindmate_data.get('categories', {})
    message_lower = user_message.lower()
    message_clean = re.sub(r"[''`]", "'", message_lower)
    message_nopunc = re.sub(r"[^\w\s]", " ", message_lower)
    message_nopunc = ' '.join(message_nopunc.split())

    best_category = 'default'
    max_score = 0

    # Crisis check FIRST (highest priority — safety critical)
    crisis_data = categories.get('crisis', {})
    for kw in crisis_data.get('keywords', []):
        if kw.lower() in message_lower or kw.lower() in message_nopunc:
            best_category = 'crisis'
            max_score = 999
            break

    if max_score < 999:
        for cat_name, cat_data in categories.items():
            if cat_name in ('default', 'crisis'):
                continue
            keywords = cat_data.get('keywords', [])
            score = 0
            for kw in keywords:
                kw_lower = kw.lower()
                kw_nopunc = re.sub(r"[^\w\s]", " ", kw_lower).strip()
                is_phrase = ' ' in kw_lower
                matched = (kw_lower in message_lower or
                          kw_nopunc in message_nopunc or
                          kw_lower in message_clean)
                if matched:
                    if is_phrase:
                        score += 5
                    elif f' {kw_lower} ' in f' {message_nopunc} ':
                        score += 3
                    else:
                        score += 1
            if score > max_score:
                max_score = score
                best_category = cat_name

    responses = categories.get(best_category, categories['default']).get('responses', [])
    chosen = random.choice(responses) if responses else "I'm here for you, {name}. Tell me more about how you're feeling."

    display_name = username.capitalize() if username and username != 'friend' else 'friend'
    chosen = chosen.replace('{name}', display_name)

    disclaimer = _mindmate_data.get('disclaimer', '')

    return {
        'answer': chosen,
        'category': best_category,
        'disclaimer': disclaimer
    }


def get_suggested_questions(language='en', limit=5):
    """Get random suggested FAQ questions for display."""
    global _faq_data

    if _faq_data is None:
        load_faqs_from_db()

    if not _faq_data:
        return []

    sample = random.sample(_faq_data, min(limit, len(_faq_data)))
    key = f'question_{language}'
    return [faq.get(key) or faq.get('question_en', '') for faq in sample]


def reload_faqs():
    """Force reload FAQs (after admin edits)."""
    global _faq_embeddings, _faq_data, _mindmate_data
    _faq_embeddings = None
    _faq_data = None
    _mindmate_data = None
    load_faqs_from_db()
