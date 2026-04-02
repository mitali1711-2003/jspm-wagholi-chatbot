"""
MindMate AI + CampusConnect AI — Main Flask Application
===================================================================
A multilingual AI chatbot for JSPM Wagholi campus queries
and mental health support (MindMate AI).
"""

import os
import json
from functools import wraps
from datetime import datetime

from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, session, flash
)

from models.database import get_db, init_db, load_dataset_to_db
from utils.auth import hash_password, check_password
from utils.nlp_engine import (
    detect_language, get_campus_response, get_mindmate_response,
    get_suggested_questions, reload_faqs
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'jspm-wagholi-mindmate-secret-2024')

# ─── Initialization ───────────────────────────────────────────────

def setup():
    """Initialize database and load JSPM Wagholi dataset."""
    init_db()

    # Load ONLY Wagholi-specific dataset
    from utils.scraper import load_wagholi_data
    load_wagholi_data()

    # Pre-load NLP models
    try:
        from utils.nlp_engine import load_faqs_from_db
        load_faqs_from_db()
    except Exception as e:
        print(f"[WARN] NLP pre-load deferred: {e}")


# ─── Auth Decorators ─────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ─── Page Routes ──────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        ip = request.remote_addr or 'unknown'
        ua = request.headers.get('User-Agent', '')[:200]

        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user and check_password(password, user['password_hash']):
            # Log successful login
            conn.execute(
                'INSERT INTO login_logs (username, ip_address, user_agent, status) VALUES (?, ?, ?, ?)',
                (username, ip, ua, 'success')
            )
            conn.commit()
            conn.close()

            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['language'] = 'en'
            return redirect(url_for('dashboard'))

        # Log failed login attempt
        conn.execute(
            'INSERT INTO login_logs (username, ip_address, user_agent, status) VALUES (?, ?, ?, ?)',
            (username, ip, ua, 'failed')
        )
        conn.commit()
        conn.close()

        flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('signup.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('signup.html')

        conn = get_db()
        existing = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()

        if existing:
            conn.close()
            flash('Username or email already exists.', 'error')
            return render_template('signup.html')

        hashed = hash_password(password)
        conn.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, hashed)
        )
        conn.commit()
        conn.close()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))


# ─── Language Selection (NEW) ─────────────────────────────────────

@app.route('/select-language')
@login_required
def select_language():
    """Language selection screen shown before chat."""
    bot = request.args.get('bot', 'campus')
    return render_template('select_language.html', bot_type=bot)


@app.route('/api/set-language', methods=['POST'])
@login_required
def api_set_language():
    """Save selected language to session."""
    data = request.get_json()
    lang = data.get('language', 'en')
    if lang not in ('en', 'hi', 'mr'):
        lang = 'en'
    session['language'] = lang
    return jsonify({'success': True, 'language': lang})


# ─── Chat Routes ──────────────────────────────────────────────────

@app.route('/chat/campus')
@login_required
def campus_chat():
    lang = session.get('language', 'en')
    return render_template('campus_chat.html',
                           username=session.get('username'),
                           selected_language=lang)


@app.route('/chat/mindmate')
@login_required
def mindmate_chat():
    lang = session.get('language', 'en')
    return render_template('mindmate_chat.html',
                           username=session.get('username'),
                           selected_language=lang)


# ─── Campus Map (NEW) ────────────────────────────────────────────

@app.route('/campus-map')
@login_required
def campus_map():
    return render_template('campus_map.html')


# ─── Contact Page (NEW) ──────────────────────────────────────────

@app.route('/contact', methods=['GET'])
@login_required
def contact_page():
    return render_template('contact.html')


@app.route('/api/contact', methods=['POST'])
@login_required
def api_contact():
    """Handle contact form submission."""
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    if not name or not email or not message:
        return jsonify({'error': 'Name, email, and message are required.'}), 400

    conn = get_db()
    conn.execute(
        '''INSERT INTO contact_messages (name, email, phone, subject, message)
           VALUES (?, ?, ?, ?, ?)''',
        (name, email, phone, subject, message)
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Your message has been sent! We will get back to you soon.'})


# ─── API Routes ───────────────────────────────────────────────────

@app.route('/api/chat/campus', methods=['POST'])
@login_required
def api_campus_chat():
    """Process a JSPM Wagholi campus chatbot query."""
    data = request.get_json()
    message = data.get('message', '').strip()
    lang = data.get('language', session.get('language', 'en'))

    if not message:
        return jsonify({'error': 'Empty message'}), 400

    # Use session language unless explicitly overridden
    if lang == 'auto':
        lang = detect_language(message)

    result = get_campus_response(message, language=lang, campus='JSPM Wagholi')

    # Save to chat history and analytics
    try:
        conn = get_db()
        conn.execute(
            '''INSERT INTO chat_history (user_id, bot_type, user_message, bot_response, language, campus)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (session['user_id'], 'campus', message, result['answer'], lang, 'JSPM Wagholi')
        )
        conn.execute(
            '''INSERT INTO analytics (query_text, matched_faq_id, bot_type, language, confidence, user_id)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (message, result.get('faq_id'), 'campus', lang, result['confidence'], session['user_id'])
        )
        conn.commit()
    except Exception as e:
        print(f"[WARN] DB write error (campus): {e}")
    finally:
        conn.close()

    return jsonify({
        'response': result['answer'],
        'language': lang,
        'confidence': round(result['confidence'], 3),
        'category': result['category']
    })


@app.route('/api/chat/mindmate', methods=['POST'])
@login_required
def api_mindmate_chat():
    """Process a MindMate AI query."""
    data = request.get_json()
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'error': 'Empty message'}), 400

    lang = session.get('language', detect_language(message))
    result = get_mindmate_response(message, language=lang, username=session.get('username', 'friend'))

    try:
        conn = get_db()
        conn.execute(
            '''INSERT INTO chat_history (user_id, bot_type, user_message, bot_response, language)
               VALUES (?, ?, ?, ?, ?)''',
            (session['user_id'], 'mindmate', message, result['answer'], lang)
        )
        conn.execute(
            '''INSERT INTO analytics (query_text, bot_type, language, confidence, user_id)
               VALUES (?, ?, ?, ?, ?)''',
            (message, 'mindmate', lang, 1.0, session['user_id'])
        )
        conn.commit()
    except Exception as e:
        print(f"[WARN] DB write error (mindmate): {e}")
    finally:
        conn.close()

    return jsonify({
        'response': result['answer'],
        'category': result['category'],
        'disclaimer': result['disclaimer']
    })


@app.route('/api/suggestions', methods=['GET'])
@login_required
def api_suggestions():
    """Get suggested FAQ questions in session language."""
    lang = request.args.get('language', session.get('language', 'en'))
    questions = get_suggested_questions(language=lang, limit=5)
    return jsonify({'suggestions': questions})


@app.route('/api/history', methods=['GET'])
@login_required
def api_history():
    """Get chat history for current user."""
    bot_type = request.args.get('bot_type', 'campus')
    conn = get_db()
    rows = conn.execute(
        '''SELECT user_message, bot_response, language, created_at
           FROM chat_history WHERE user_id = ? AND bot_type = ?
           ORDER BY created_at DESC LIMIT 50''',
        (session['user_id'], bot_type)
    ).fetchall()
    conn.close()
    return jsonify({'history': [dict(r) for r in rows]})


@app.route('/api/review', methods=['POST'])
@login_required
def api_submit_review():
    """Submit a review when user ends the conversation."""
    data = request.get_json()
    rating = data.get('rating', 0)
    feedback = data.get('feedback', '').strip()
    bot_type = data.get('bot_type', 'campus')

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be 1-5'}), 400

    try:
        conn = get_db()
        conn.execute(
            '''INSERT INTO reviews (user_id, username, bot_type, rating, feedback)
               VALUES (?, ?, ?, ?, ?)''',
            (session['user_id'], session.get('username', ''), bot_type, rating, feedback)
        )
        conn.commit()
    except Exception as e:
        print(f"[WARN] Review save error: {e}")
    finally:
        conn.close()

    return jsonify({'success': True, 'message': 'Thank you for your feedback!'})


# ─── Admin Routes ─────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_panel():
    return render_template('admin.html')


@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    return render_template('admin_analytics.html')


@app.route('/admin/security')
@admin_required
def admin_security():
    return render_template('admin_security.html')


@app.route('/admin/conversations')
@admin_required
def admin_conversations():
    return render_template('admin_conversations.html')


@app.route('/api/admin/conversations', methods=['GET'])
@admin_required
def api_admin_conversations():
    """Get all questions asked to bots, with user info and reviews."""
    conn = get_db()

    bot_filter = request.args.get('bot', 'all')
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    # Build query based on filter
    where = ""
    params = []
    if bot_filter in ('campus', 'mindmate'):
        where = "WHERE ch.bot_type = ?"
        params = [bot_filter]

    # All conversations with user info
    chats = conn.execute(f'''
        SELECT ch.id, ch.user_message, ch.bot_response, ch.bot_type,
               ch.language, ch.created_at, u.username
        FROM chat_history ch
        JOIN users u ON ch.user_id = u.id
        {where}
        ORDER BY ch.created_at DESC
        LIMIT ? OFFSET ?
    ''', params + [per_page, offset]).fetchall()

    # Total count
    total = conn.execute(f'''
        SELECT COUNT(*) as c FROM chat_history ch {where}
    ''', params).fetchone()

    # Most asked questions (top 20)
    top_questions = conn.execute('''
        SELECT user_message, bot_type, COUNT(*) as count,
               GROUP_CONCAT(DISTINCT u.username) as users
        FROM chat_history ch
        JOIN users u ON ch.user_id = u.id
        GROUP BY user_message, bot_type
        ORDER BY count DESC LIMIT 20
    ''').fetchall()

    # Questions per user
    user_activity = conn.execute('''
        SELECT u.username, COUNT(*) as total_questions,
               SUM(CASE WHEN ch.bot_type='campus' THEN 1 ELSE 0 END) as campus_q,
               SUM(CASE WHEN ch.bot_type='mindmate' THEN 1 ELSE 0 END) as mindmate_q
        FROM chat_history ch
        JOIN users u ON ch.user_id = u.id
        GROUP BY u.username
        ORDER BY total_questions DESC
    ''').fetchall()

    # All reviews
    reviews = conn.execute('''
        SELECT r.*, u.username
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        ORDER BY r.created_at DESC LIMIT 50
    ''').fetchall()

    # Average ratings
    avg_campus = conn.execute(
        "SELECT AVG(rating) as avg, COUNT(*) as c FROM reviews WHERE bot_type='campus'"
    ).fetchone()
    avg_mindmate = conn.execute(
        "SELECT AVG(rating) as avg, COUNT(*) as c FROM reviews WHERE bot_type='mindmate'"
    ).fetchone()

    conn.close()

    return jsonify({
        'conversations': [dict(c) for c in chats],
        'total': total['c'],
        'page': page,
        'per_page': per_page,
        'top_questions': [dict(q) for q in top_questions],
        'user_activity': [dict(u) for u in user_activity],
        'reviews': [dict(r) for r in reviews],
        'avg_ratings': {
            'campus': round(avg_campus['avg'] or 0, 1),
            'campus_count': avg_campus['c'],
            'mindmate': round(avg_mindmate['avg'] or 0, 1),
            'mindmate_count': avg_mindmate['c']
        }
    })


@app.route('/api/admin/security-logs', methods=['GET'])
@admin_required
def api_security_logs():
    """Get login logs and detect suspicious activity."""
    conn = get_db()

    # All recent login logs (last 200)
    logs = conn.execute('''
        SELECT id, username, ip_address, user_agent, status, created_at
        FROM login_logs ORDER BY created_at DESC LIMIT 200
    ''').fetchall()

    # Failed attempts grouped by IP (last 24 hours)
    suspicious_ips = conn.execute('''
        SELECT ip_address, COUNT(*) as attempts, GROUP_CONCAT(DISTINCT username) as usernames
        FROM login_logs
        WHERE status = 'failed' AND created_at >= DATETIME('now', '-24 hours')
        GROUP BY ip_address
        HAVING attempts >= 3
        ORDER BY attempts DESC
    ''').fetchall()

    # Failed attempts grouped by username (last 24 hours)
    suspicious_users = conn.execute('''
        SELECT username, COUNT(*) as attempts, GROUP_CONCAT(DISTINCT ip_address) as ips
        FROM login_logs
        WHERE status = 'failed' AND created_at >= DATETIME('now', '-24 hours')
        GROUP BY username
        HAVING attempts >= 3
        ORDER BY attempts DESC
    ''').fetchall()

    # Summary stats
    total_logins = conn.execute(
        "SELECT COUNT(*) as c FROM login_logs WHERE status = 'success'"
    ).fetchone()
    total_failed = conn.execute(
        "SELECT COUNT(*) as c FROM login_logs WHERE status = 'failed'"
    ).fetchone()
    failed_24h = conn.execute(
        "SELECT COUNT(*) as c FROM login_logs WHERE status = 'failed' AND created_at >= DATETIME('now', '-24 hours')"
    ).fetchone()
    unique_ips = conn.execute(
        "SELECT COUNT(DISTINCT ip_address) as c FROM login_logs"
    ).fetchone()

    # Hourly login attempts (last 24 hours) for chart
    hourly = conn.execute('''
        SELECT strftime('%H', created_at) as hour, status, COUNT(*) as count
        FROM login_logs
        WHERE created_at >= DATETIME('now', '-24 hours')
        GROUP BY hour, status
        ORDER BY hour
    ''').fetchall()

    conn.close()

    return jsonify({
        'logs': [dict(l) for l in logs],
        'suspicious_ips': [dict(s) for s in suspicious_ips],
        'suspicious_users': [dict(s) for s in suspicious_users],
        'stats': {
            'total_logins': total_logins['c'],
            'total_failed': total_failed['c'],
            'failed_24h': failed_24h['c'],
            'unique_ips': unique_ips['c']
        },
        'hourly': [dict(h) for h in hourly]
    })


@app.route('/api/admin/faqs', methods=['GET'])
@admin_required
def api_get_faqs():
    conn = get_db()
    faqs = conn.execute('SELECT * FROM faqs ORDER BY category, id').fetchall()
    conn.close()
    return jsonify({'faqs': [dict(f) for f in faqs]})


@app.route('/api/admin/faqs', methods=['POST'])
@admin_required
def api_add_faq():
    data = request.get_json()
    conn = get_db()
    conn.execute('''
        INSERT INTO faqs (category, question_en, question_hi, question_mr,
                          answer_en, answer_hi, answer_mr, campus)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('category', 'general'),
        data.get('question_en', ''),
        data.get('question_hi', ''),
        data.get('question_mr', ''),
        data.get('answer_en', ''),
        data.get('answer_hi', ''),
        data.get('answer_mr', ''),
        'JSPM University - Wagholi Campus'
    ))
    conn.commit()
    conn.close()
    reload_faqs()
    return jsonify({'success': True, 'message': 'FAQ added successfully'})


@app.route('/api/admin/faqs/<int:faq_id>', methods=['PUT'])
@admin_required
def api_update_faq(faq_id):
    data = request.get_json()
    conn = get_db()
    conn.execute('''
        UPDATE faqs SET category=?, question_en=?, question_hi=?, question_mr=?,
                        answer_en=?, answer_hi=?, answer_mr=?, updated_at=?
        WHERE id=?
    ''', (
        data.get('category', 'general'),
        data.get('question_en', ''),
        data.get('question_hi', ''),
        data.get('question_mr', ''),
        data.get('answer_en', ''),
        data.get('answer_hi', ''),
        data.get('answer_mr', ''),
        datetime.now().isoformat(),
        faq_id
    ))
    conn.commit()
    conn.close()
    reload_faqs()
    return jsonify({'success': True, 'message': 'FAQ updated'})


@app.route('/api/admin/faqs/<int:faq_id>', methods=['DELETE'])
@admin_required
def api_delete_faq(faq_id):
    conn = get_db()
    conn.execute('DELETE FROM faqs WHERE id = ?', (faq_id,))
    conn.commit()
    conn.close()
    reload_faqs()
    return jsonify({'success': True, 'message': 'FAQ deleted'})


@app.route('/api/admin/analytics', methods=['GET'])
@admin_required
def api_analytics():
    conn = get_db()

    top_queries = conn.execute('''
        SELECT query_text, COUNT(*) as count, bot_type
        FROM analytics GROUP BY query_text, bot_type
        ORDER BY count DESC LIMIT 20
    ''').fetchall()

    lang_stats = conn.execute('''
        SELECT language, COUNT(*) as count
        FROM analytics GROUP BY language ORDER BY count DESC
    ''').fetchall()

    daily_usage = conn.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as count, bot_type
        FROM analytics WHERE created_at >= DATE('now', '-30 days')
        GROUP BY DATE(created_at), bot_type ORDER BY date
    ''').fetchall()

    category_stats = conn.execute('''
        SELECT bot_type, COUNT(*) as count
        FROM analytics GROUP BY bot_type
    ''').fetchall()

    total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()
    total_chats = conn.execute('SELECT COUNT(*) as count FROM chat_history').fetchone()

    conn.close()

    return jsonify({
        'top_queries': [dict(q) for q in top_queries],
        'language_stats': [dict(l) for l in lang_stats],
        'daily_usage': [dict(d) for d in daily_usage],
        'category_stats': [dict(c) for c in category_stats],
        'total_users': total_users['count'],
        'total_chats': total_chats['count']
    })


@app.route('/api/admin/upload-dataset', methods=['POST'])
@admin_required
def api_upload_dataset():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if not file.filename.endswith('.json'):
        return jsonify({'error': 'Only JSON files allowed'}), 400
    save_path = os.path.join('database', f'campus_{file.filename}')
    file.save(save_path)
    success = load_dataset_to_db(save_path)
    if success:
        reload_faqs()
    return jsonify({'success': success, 'message': 'Dataset uploaded and loaded'})


# ─── Initialization (runs for both gunicorn and dev server) ──────

setup()

# ─── Run ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
