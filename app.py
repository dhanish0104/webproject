from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort
from datetime import datetime
from types import SimpleNamespace
import random
import string
import os
import threading
import requests
from pymongo import MongoClient, ASCENDING, DESCENDING, ReturnDocument
from pymongo.errors import PyMongoError

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

# MongoDB Configuration
# On Render: set MONGO_URI in the Environment Variables dashboard.
# For local development: defaults to localhost if MONGO_URI is not set.
mongo_uri = os.environ['MONGO_URI'] if 'MONGO_URI' in os.environ else 'mongodb://localhost:27017'
mongo_db_name = os.environ.get('MONGO_DB_NAME', 'government_complaint_portal')
mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
mongo_db = mongo_client[mongo_db_name]
users_col = mongo_db.users
complaints_col = mongo_db.complaints
history_col = mongo_db.complaint_history
counters_col = mongo_db.counters

# --- Test MongoDB Connection ---
import sys
try:
    print("--------------------------------------------------")
    print(f"Attempting to connect to MongoDB...")
    # Ping the server to check connection
    mongo_client.admin.command('ping')
    print("✅ SUCCESS: Successfully connected to MongoDB Atlas!")
    print(f"Connected to database: {mongo_db_name}")
    print("--------------------------------------------------")
except Exception as e:
    print("--------------------------------------------------")
    print(f"❌ CRITICAL ERROR: Failed to connect to MongoDB Atlas!")
    print(f"Error Details: {e}")
    print("Please check: ")
    print("1. Your MONGO_URI username and password are correct.")
    print("2. You have whitelisted all IPs (0.0.0.0/0) in MongoDB Atlas Network Access.")
    print("--------------------------------------------------")

# Admin Credentials
app.config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin123')
# --- Data Structure for Categories and Topics ---
COMPLAINT_CATEGORIES = {
    'Infrastructure': [
        {'name': 'Pothole-filled Roads', 'image': '/static/images/infra_pothole.jpg'},
        {'name': 'Damaged Highways', 'image': '/static/images/infra_highway.jpg'},
        {'name': 'Broken Bridges', 'image': '/static/images/infra_bridge.jpg'},
        {'name': 'Incomplete Roads', 'image': '/static/images/infra_incomplete.jpg'},
        {'name': 'Flooded Roads', 'image': '/static/images/infra_flooded.jpg'},
        {'name': 'Missing Street Lights', 'image': '/static/images/infra_streetlight.jpg'},
        {'name': 'Damaged Footpaths', 'image': '/static/images/infra_footpath.jpg'},
        {'name': 'Unsafe Flyovers', 'image': '/static/images/infra_flyover.jpg'},
        {'name': 'Encroachments', 'image': '/static/images/infra_encroachment.jpg'}
    ],
    'Water & Sanitation': [
        {'name': 'Drinking Water Shortage', 'image': '/static/images/water_shortage.jpg'},
        {'name': 'Contaminated Water', 'image': '/static/images/water_dirty.jpg'},
        {'name': 'Irregular Supply', 'image': '/static/images/water_tanker.jpg'},
        {'name': 'Pipeline Leakage', 'image': '/static/images/water_leak.jpg'},
        {'name': 'Open Drains', 'image': '/static/images/water_drain.jpg'},
        {'name': 'Sewage Overflow', 'image': '/static/images/water_overflow.jpg'},
        {'name': 'Public Toilet Issues', 'image': 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&q=80&w=400'},
        {'name': 'River Pollution', 'image': '/static/images/water_riverflow.jpg'}
    ],
    'Electricity': [
       {'name': 'Power Outages', 'image': '/static/images/elec_outage.jpg'},
       {'name': 'Voltage Fluctuation', 'image': '/static/images/elec_voltage.jpg'},
       {'name': 'Transformer Issue', 'image': '/static/images/elec_transformer.jpg'},
       {'name': 'Faulty Meter', 'image': '/static/images/elec_meter.jpg'},
       {'name': 'Street Light Failure', 'image': '/static/images/elec_streetlight.jpg'}
    ],
    'Healthcare': [
        {'name': 'Doctor Shortage', 'image': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&q=80&w=400'},
        {'name': 'Hospital Hygiene', 'image': 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&q=80&w=400'},
        {'name': 'Medicine Shortage', 'image': 'https://images.unsplash.com/photo-1585435557343-3b092031a831?auto=format&fit=crop&q=80&w=400'},
        {'name': 'Overcrowding', 'image': '/static/images/health_crowd.jpg'},
        {'name': 'Ambulance Delay', 'image': '/static/images/health_ambulance.jpg'},
        {'name': 'Bed/ICU Shortage', 'image': '/static/images/health_beds.jpg'}
    ],
    'Education': [
       {'name': 'School Infrastructure', 'image': '/static/images/edu_infrastructure.jpg'},
       {'name': 'Teacher Shortage', 'image': '/static/images/edu_teacher.jpg'},
       {'name': 'Outdated Syllabus', 'image': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&q=80&w=400'},
       {'name': 'Scholarship Delay', 'image': 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&q=80&w=400'},
       {'name': 'Midday Meal Issue', 'image': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&q=80&w=400'}
    ],
    'Housing': [
       {'name': 'Illegal Construction', 'image': '/static/images/housing_collapse.jpg'},
       {'name': 'Slum Rehabilitation', 'image': '/static/images/housing_slum.jpg'},
       {'name': 'Poor Housing', 'image': '/static/images/housing_dilapidated.jpg'},
       {'name': 'Land Encroachment', 'image': '/static/images/housing_encroachment.jpg'}
    ],
    'Waste Mgmt': [
       {'name': 'Garbage Not Collected', 'image': 'https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&q=80&w=400'},
       {'name': 'Overflowing Dustbins', 'image': 'https://images.unsplash.com/photo-1605600659908-0ef719419d41?auto=format&fit=crop&q=80&w=400'},
       {'name': 'Plastic Waste', 'image': 'https://images.unsplash.com/photo-1611284446314-60a58ac0deb9?auto=format&fit=crop&q=80&w=400'},
        {'name': 'Garbage Burning', 'image': '/static/images/waste_burning.jpg'}
    ],
    'Transport': [
       {'name': 'Traffic Congestion', 'image': '/static/images/trans_traffic.jpg'},
       {'name': 'Broken Signals', 'image': '/static/images/trans_signal.jpg'},
       {'name': 'Unsafe Bus Stops', 'image': '/static/images/trans_road.jpg'},
       {'name': 'Overcrowding', 'image': '/static/images/trans_bus.jpg'}
    ],
    'Law & Order': [
       {'name': 'Police Delay', 'image': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&q=80&w=400'},
       {'name': 'Women Safety', 'image': '/static/images/law_womens_safety.jpg'},
       {'name': 'Street Crime', 'image': '/static/images/law_street_crime.jpg'},
       {'name': 'Noise Pollution', 'image': '/static/images/law_noise_pollution.jpg'}
    ],
    'Environment': [
       {'name': 'Air Pollution', 'image': '/static/images/env_air.jpg'},
       {'name': 'Water Pollution', 'image': '/static/images/env_water.jpg'},
       {'name': 'Deforestation', 'image': '/static/images/env_deforestation.jpg'},
       {'name': 'Sand Mining', 'image': '/static/images/env_sand.jpg'}
    ]
}

# --- Helper Functions ---
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def send_brevo_email(email, subject, html_content):
    api_key = os.environ.get("BREVO_API_KEY")
    if not api_key:
        print("BREVO ERROR: BREVO_API_KEY is not configured")
        return False

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    data = {
        "sender": {"email": os.environ.get("BREVO_SENDER_EMAIL", "dhanishkanth1122@gmail.com")},
        "to": [{"email": email}],
        "subject": subject,
        "htmlContent": html_content
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"BREVO RESPONSE [{response.status_code}]: {response.text}")
        return response.status_code == 201
    except Exception as e:
        print(f"BREVO ERROR: {e}")
        return False


def send_otp_email(email, otp):
    subject = "Your Login OTP"
    html_content = f"<h2>Your OTP is: {otp}</h2>"
    return send_brevo_email(email, subject, html_content)


class AttrDict(SimpleNamespace):
    def get(self, key, default=None):
        return getattr(self, key, default)


def to_obj(doc):
    if not doc:
        return None
    data = dict(doc)
    data['mongo_id'] = str(data.pop('_id', ''))
    if 'email' in data and not data.get('username'):
        data['username'] = data['email'].split('@')[0]
    return AttrDict(**data)


def next_sequence(name):
    counter = counters_col.find_one_and_update(
        {'_id': name},
        {'$inc': {'value': 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return counter['value']


def get_user_by_id(user_id):
    try:
        return to_obj(users_col.find_one({'id': int(user_id)}))
    except (TypeError, ValueError):
        return None


def get_user_doc_by_id(user_id):
    try:
        return users_col.find_one({'id': int(user_id)})
    except (TypeError, ValueError):
        return None


def get_complaint_doc(complaint_id):
    try:
        return complaints_col.find_one({'id': int(complaint_id)})
    except (TypeError, ValueError):
        return None


def complaint_with_related(doc, include_history=True):
    complaint = to_obj(doc)
    if not complaint:
        return None

    complaint.user = get_user_by_id(getattr(complaint, 'user_id', None))
    if include_history:
        events = history_col.find({'complaint_id': complaint.id}).sort('timestamp', DESCENDING)
        complaint.history = [to_obj(event) for event in events]
    else:
        complaint.history = []
    return complaint


def seed_data():
    """Seeds MongoDB with sample users if the users collection is empty."""
    if users_col.count_documents({}) > 0:
        return

    print("Seeding synthetic MongoDB users...")
    sample_users = [
        {"aadhaar": "111122223333", "phone": "9876543210", "email": "user1@example.com"},
        {"aadhaar": "444455556666", "phone": "9123456780", "email": "user2@example.com"},
        {"aadhaar": "777788889999", "phone": "9988776655", "email": "dhanishkanth1122@gmail.com"}
    ]
    for user in sample_users:
        user['id'] = next_sequence('users')
        user['username'] = user['email'].split('@')[0]
        user['otp'] = None
        user['created_at'] = datetime.utcnow()
    users_col.insert_many(sample_users)
    print("MongoDB seeding complete.")


def init_mongo():
    users_col.create_index([('id', ASCENDING)], unique=True)
    users_col.create_index([('aadhaar', ASCENDING)], unique=True)
    users_col.create_index([('phone', ASCENDING)], unique=True)
    users_col.create_index([('email', ASCENDING)], unique=True)
    complaints_col.create_index([('id', ASCENDING)], unique=True)
    complaints_col.create_index([('user_id', ASCENDING)])
    complaints_col.create_index([('status', ASCENDING)])
    history_col.create_index([('complaint_id', ASCENDING)])
    seed_data()


try:
    init_mongo()
except PyMongoError as e:
    print(f"MongoDB initialization skipped: {e}")


# Helper to flatten categories for easy lookup
TOPIC_IMAGE_MAP = {}
for cat, topics in COMPLAINT_CATEGORIES.items():
    for topic in topics:
        TOPIC_IMAGE_MAP[topic['name']] = topic['image']


@app.context_processor
def utility_processor():
    def get_topic_image(topic_name):
        return TOPIC_IMAGE_MAP.get(topic_name, 'https://placehold.co/600x400?text=Grievance')
    return dict(get_topic_image=get_topic_image)


# --- Routes ---
@app.route('/')
def home():
    try:
        print(f"Home route accessed. User count: {users_col.count_documents({})}")
    except Exception as e:
        print(f"MongoDB Error on home: {e}")

    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user = get_user_by_id(session.get('user_id'))
    print("SESSION USER ID:", session.get('user_id'))
    print("USER OBJECT:", user)

    if not user:
        session.clear()
        return redirect(url_for('home'))

    complaint_docs = list(complaints_col.find({'user_id': user.id}).sort('id', ASCENDING))
    complaints = [complaint_with_related(doc, include_history=False) for doc in complaint_docs]

    total_complaints = len(complaints)
    pending_count = sum(1 for c in complaints if c.status == 'Pending')
    in_progress_count = sum(1 for c in complaints if c.status == 'In Progress')
    resolved_count = sum(1 for c in complaints if c.status == 'Resolved')
    recent_complaints = list(reversed(complaints))[:5]

    success_docs = complaints_col.find({'status': 'Resolved'}).sort('id', DESCENDING).limit(6)
    success_stories = [complaint_with_related(doc, include_history=False) for doc in success_docs]

    print(f"DIAGNOSTIC: User {user.id} has {resolved_count} resolved complaints.")
    print(f"DIAGNOSTIC: Total resolved in DB (success_stories): {complaints_col.count_documents({'status': 'Resolved'})}")

    return render_template('dashboard.html',
                         user=user,
                         total_complaints=total_complaints,
                         pending_count=pending_count,
                         in_progress_count=in_progress_count,
                         resolved_count=resolved_count,
                         recent_complaints=recent_complaints,
                         success_stories=success_stories)


@app.route('/raise-complaint')
def raise_complaint():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    user = get_user_by_id(session['user_id'])
    return render_template('raise_complaint.html', user=user)


@app.route('/category/<category_name>')
def category_complaints(category_name):
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user = get_user_by_id(session['user_id'])
    topics = COMPLAINT_CATEGORIES.get(category_name, [])
    return render_template('category_complaints.html', user=user, category=category_name, topics=topics)


@app.route('/complaint')
def complaint():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('complaint.html', google_maps_api_key=google_maps_api_key)


@app.route('/submit-complaint', methods=['POST'])
def submit_complaint():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or {}
    try:
        new_complaint = {
            'id': next_sequence('complaints'),
            'category': data.get('category'),
            'topic': data.get('topic'),
            'state': data.get('state'),
            'district': data.get('district'),
            'area': data.get('area'),
            'description': data.get('description'),
            'admin_comment': None,
            'user_feedback': None,
            'status': 'Pending',
            'user_id': int(session['user_id']),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        complaints_col.insert_one(new_complaint)
    except Exception as e:
        print(f"Error saving complaint: {e}")
        return jsonify({'success': False, 'message': 'Database Error'}), 500

    try:
        user = get_user_by_id(session['user_id'])
        if user and user.email:
            subject = 'Complaint Registered Successfully - National Portal'
            html_content = render_template('email_confirmation.html',
                                       category=new_complaint['category'],
                                       complaint_id=new_complaint['id'])
            email_thread = threading.Thread(target=send_brevo_email, args=(user.email, subject, html_content))
            email_thread.start()
    except Exception as e:
        print(f"Failed to initiate confirmation email: {e}")

    return jsonify({'success': True, 'message': 'Complaint submitted successfully. Confirmation email sent.'})


@app.route('/submit-feedback/<int:id>', methods=['POST'])
def submit_feedback(id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or {}
    feedback = data.get('feedback')
    complaint_doc = get_complaint_doc(id)

    if not complaint_doc or complaint_doc.get('user_id') != int(session['user_id']):
        return jsonify({'success': False, 'message': 'Complaint not found'}), 404

    if complaint_doc.get('status') != 'Resolved':
        return jsonify({'success': False, 'message': 'Can only give feedback on resolved complaints'}), 400

    complaints_col.update_one({'id': id}, {'$set': {'user_feedback': feedback, 'updated_at': datetime.utcnow()}})
    return jsonify({'success': True, 'message': 'Thank you for your feedback!'})


@app.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        print("SEND OTP ROUTE HIT")
        data = request.get_json(silent=True)
        print("DATA:", data)

        if not data:
            return jsonify({'success': False, 'message': 'No JSON received'}), 400

        email = (data.get('email') or "").strip()
        aadhaar = (data.get('aadhaar') or "").strip()
        phone = (data.get('phone') or "").strip()
        print("INPUT:", email, aadhaar, phone)

        user = users_col.find_one({'email': email, 'aadhaar': aadhaar, 'phone': phone})
        print("USER:", user)

        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found. Please register or enter the exact Aadhaar, phone, and email used during registration.'
            }), 404

        otp = generate_otp()
        users_col.update_one({'id': user['id']}, {'$set': {'otp': otp}})
        print("OTP GENERATED:", otp)

        try:
            print(f"TRYING TO SEND EMAIL TO: {email}")
            if send_otp_email(email, otp):
                print("EMAIL SENT SUCCESSFULLY")
                return jsonify({'success': True, 'message': 'OTP sent'})

            print("EMAIL SEND FAILED")
            return jsonify({
                'success': True,
                'message': f'Email service unavailable. Your OTP is {otp}',
                'dev_otp': otp
            })
        except Exception:
            import traceback
            print("MAIL ERROR FULL:", traceback.format_exc())
            return jsonify({
                'success': True,
                'message': f'System Partial Error: Your OTP is {otp}',
                'dev_otp': otp
            })

    except Exception as e:
        import traceback
        print("ERROR:", traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        aadhaar = (request.form.get('aadhaar') or '').strip()
        phone = (request.form.get('phone') or '').strip()
        email = (request.form.get('email') or '').strip()

        user = users_col.find_one({'$or': [{'aadhaar': aadhaar}, {'phone': phone}, {'email': email}]})
        if user:
            return render_template('register.html', message="User already exists with these details!")

        new_user = {
            'id': next_sequence('users'),
            'aadhaar': aadhaar,
            'phone': phone,
            'email': email,
            'username': email.split('@')[0],
            'otp': None,
            'created_at': datetime.utcnow()
        }
        users_col.insert_one(new_user)
        return render_template('register.html', message="Registration Successful! You can now Login.")

    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    entered_otp = (data.get('otp') or "").strip()
    aadhaar = (data.get('aadhaar') or "").strip()
    phone = (data.get('phone') or "").strip()
    email = (data.get('email') or "").strip()

    if not (aadhaar and phone and email and entered_otp):
         return jsonify({'success': False, 'message': 'All fields are required'}), 400

    user = users_col.find_one({'aadhaar': aadhaar, 'phone': phone, 'email': email})

    if user:
        print("DB OTP:", user.get('otp'))
        print("ENTERED OTP:", entered_otp)
    else:
        print("USER NOT FOUND IN DB")

    if not user or str(user.get('otp')) != str(entered_otp):
        return jsonify({'success': False, 'message': 'Invalid OTP'}), 401

    session['user_id'] = user['id']
    users_col.update_one({'id': user['id']}, {'$set': {'otp': None}})
    return jsonify({'success': True, 'redirect': url_for('dashboard')})


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    user = get_user_by_id(session['user_id'])
    return render_template('profile.html', user=user)


@app.route('/contact')
def contact():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return render_template('contact.html')


@app.route('/my-complaints')
def my_complaints():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = int(session['user_id'])
    complaint_docs = complaints_col.find({'user_id': user_id}).sort('id', DESCENDING)
    complaints = [complaint_with_related(doc, include_history=False) for doc in complaint_docs]
    return render_template('my_complaints.html', complaints=complaints)


# --- Admin Routes ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html', error="Invalid Credentials")

    return render_template('admin_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    total_complaints = complaints_col.count_documents({})
    pending_complaints = complaints_col.count_documents({'status': 'Pending'})
    in_progress_complaints = complaints_col.count_documents({'status': 'In Progress'})
    resolved_complaints = complaints_col.count_documents({'status': 'Resolved'})
    recent_docs = complaints_col.find({}).sort('id', DESCENDING).limit(5)
    recent_complaints = [complaint_with_related(doc, include_history=False) for doc in recent_docs]

    stats = {
        'total': total_complaints,
        'pending': pending_complaints,
        'in_progress': in_progress_complaints,
        'resolved': resolved_complaints
    }
    return render_template('admin_dashboard.html', stats=stats, recent_complaints=recent_complaints, active_page='dashboard')


@app.route('/admin/complaints')
def admin_complaints():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    status_filter = request.args.get('status')
    active_page = 'all_complaints'
    if status_filter == 'Pending':
        active_page = 'pending'
    elif status_filter == 'In Progress':
        active_page = 'in_progress'
    elif status_filter == 'Resolved':
        active_page = 'resolved'

    query = {'status': status_filter} if status_filter else {}
    complaint_docs = complaints_col.find(query).sort('id', DESCENDING)
    complaints = [complaint_with_related(doc, include_history=False) for doc in complaint_docs]
    return render_template('admin_complaints.html', complaints=complaints, current_filter=status_filter, active_page=active_page)


@app.route('/admin/users')
def admin_users():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    users = [to_obj(user) for user in users_col.find({}).sort('id', ASCENDING)]
    return render_template('admin_users.html', users=users, active_page='users')


@app.route('/admin/complaint/<int:id>')
def admin_complaint_details(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    complaint = complaint_with_related(get_complaint_doc(id), include_history=True)
    if not complaint:
        abort(404)
    return render_template('admin_complaint_details.html', complaint=complaint, active_page='all_complaints')


@app.route('/admin/update-status/<int:id>', methods=['POST'])
def update_status(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    complaint_doc = get_complaint_doc(id)
    if not complaint_doc:
        abort(404)

    new_status = request.form.get('status')
    admin_comment = request.form.get('admin_comment')
    update_fields = {'status': new_status, 'updated_at': datetime.utcnow()}
    if admin_comment:
        update_fields['admin_comment'] = admin_comment

    complaints_col.update_one({'id': id}, {'$set': update_fields})

    try:
        history_col.insert_one({
            'id': next_sequence('complaint_history'),
            'complaint_id': id,
            'status': new_status,
            'comment': admin_comment,
            'timestamp': datetime.utcnow()
        })
    except Exception as e:
        print(f"Error creating history: {e}")

    try:
        complaint = complaint_with_related(get_complaint_doc(id), include_history=False)
        if complaint and complaint.user and complaint.user.email:
            subject = f'Update on Complaint #{complaint.id}: {new_status}'
            topic_image = TOPIC_IMAGE_MAP.get(complaint.topic, 'https://placehold.co/600x400?text=Grievance')
            html_content = render_template('email_status_update.html',
                                         complaint=complaint,
                                         topic_image=topic_image,
                                         has_attachment=False)
            email_thread = threading.Thread(target=send_brevo_email, args=(complaint.user.email, subject, html_content))
            email_thread.start()
    except Exception as e:
        print(f"Failed to send status email: {e}")

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')