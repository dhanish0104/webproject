from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import random
import string
import os
import threading

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

# Database Configuration
os.makedirs('/data', exist_ok=True)

db_path = '/data/database_v2.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Admin Credentials
app.config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'dhanishkanth1122@gmail.com') # Replace with your email
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'hoev vokh vdjb hzxo') # Replace with your App Password
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

db = SQLAlchemy(app)
mail = Mail(app)

# --- Database Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aadhaar = db.Column(db.String(12), unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    otp = db.Column(db.String(6), nullable=True) # Store OTP in DB

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(100), nullable=False) # Specific issue (e.g. Potholes)
    state = db.Column(db.String(50), nullable=True)
    district = db.Column(db.String(50), nullable=True)
    area = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True) # User's details
    admin_comment = db.Column(db.Text, nullable=True) # Actual Admin Response
    user_feedback = db.Column(db.Text, nullable=True) # Feedback from user on resolved issue
    status = db.Column(db.String(20), default='Pending')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('complaints', lazy=True))
    history = db.relationship('ComplaintHistory', backref='complaint', lazy=True, order_by="desc(ComplaintHistory.timestamp)")

class ComplaintHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    status = db.Column(db.String(50))
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ... (Categories Data) ...

# ... (Routes) ...

@app.route('/submit-complaint', methods=['POST'])
def submit_complaint():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.json
    try:
        new_complaint = Complaint(
            category=data.get('category'),
            topic=data.get('topic'), # Capture the specific topic
            state=data.get('state'),
            district=data.get('district'),
            area=data.get('area'),
            description=data.get('description'),
            # We treat 'solution' from form as just part of description or ignore it to avoid confusion 
            # for now, let's just store user details in description.
            user_id=session['user_id']
        )
        db.session.add(new_complaint)
        db.session.commit()
    except Exception as e:
        print(f"Error saving complaint: {e}")
        return jsonify({'success': False, 'message': 'Database Error'}), 500
    
    # Send Confirmation Email (Async)
    try:
        user = db.session.get(User, session['user_id'])
        if user and user.email:
            msg = Message('Complaint Registered Successfully - National Portal', recipients=[user.email])
            msg.html = render_template('email_confirmation.html', 
                                       category=new_complaint.category, 
                                       complaint_id=new_complaint.id)
            
            email_thread = threading.Thread(target=send_async_email, args=(app, msg))
            email_thread.start()
            
    except Exception as e:
        print(f"Failed to initiate confirmation email: {e}")

    return jsonify({'success': True, 'message': 'Complaint submitted successfully. Confirmation email sent.'})

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

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

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

def seed_data():
    """Seeds the database with synthetic users if empty."""
    if User.query.first() is None:
        print("Seeding synthetic users...")
        users = [
            User(aadhaar="111122223333", phone="9876543210", email="user1@example.com"),
            User(aadhaar="444455556666", phone="9123456780", email="user2@example.com"),
            User(aadhaar="777788889999", phone="9988776655", email="dhanishkanth1122@gmail.com") # Custom one
        ]
        db.session.add_all(users)
        db.session.commit()
        print("Seeding complete.")

with app.app_context():
    db.create_all()
    if User.query.count() == 0:
        seed_data()

# --- Routes ---

@app.route('/')
def home():
    # Diagnostic print for logs
    try:
        print(f"Home route accessed. DB count: {User.query.count()}")
    except Exception as e:
        print(f"DB Error on home: {e}")

    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/test-db')
def test_db():
    """Temporary route to verify DB is writable."""
    try:
        test_user = User(
            aadhaar="123456789012", 
            phone="9999999999", 
            email="test@example.com"
        )
        db.session.add(test_user)
        db.session.commit()
        return f"User added! Total users now: {User.query.count()}"
    except Exception as e:
        return f"Database Error: {e}"

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    user = User.query.get(session['user_id'])
    complaints = Complaint.query.filter_by(user_id=user.id).all()
    
    # Calculate Stats
    total_complaints = len(complaints)
    pending_count = sum(1 for c in complaints if c.status == 'Pending')
    in_progress_count = sum(1 for c in complaints if c.status == 'In Progress')
    resolved_count = sum(1 for c in complaints if c.status == 'Resolved')
    
    # Get recent complaints (last 5, newer first)
    recent_complaints = complaints[::-1][:5]
    
    # Get Success Stories (Recent Resolved Complaints)
    all_resolved = Complaint.query.filter_by(status='Resolved').order_by(Complaint.id.desc()).all()
    success_stories = all_resolved[:6]
    
    print(f"DIAGNOSTIC: User {user.id} has {resolved_count} resolved complaints.")
    print(f"DIAGNOSTIC: Total resolved in DB (success_stories): {len(all_resolved)}")
    
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
    user = User.query.get(session['user_id'])
    return render_template('raise_complaint.html', user=user)

@app.route('/category/<category_name>')
def category_complaints(category_name):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    user = User.query.get(session['user_id'])
    
    # Get topics for this category, defaulting to empty list if not found
    topics = COMPLAINT_CATEGORIES.get(category_name, [])
    
    return render_template('category_complaints.html', user=user, category=category_name, topics=topics)

@app.route('/complaint')
def complaint():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return render_template('complaint.html')

@app.route('/submit-feedback/<int:id>', methods=['POST'])
def submit_feedback(id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    feedback = data.get('feedback')
    
    complaint = db.session.get(Complaint, id)
    if not complaint or complaint.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Complaint not found'}), 404
        
    if complaint.status != 'Resolved':
        return jsonify({'success': False, 'message': 'Can only give feedback on resolved complaints'}), 400
        
    complaint.user_feedback = feedback
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Thank you for your feedback!'})

@app.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json(force=True)
        print("DATA:", data)

        if not data:
            return jsonify({'success': False, 'message': 'No data received'}), 400

        email = data.get('email')
        aadhaar = data.get('aadhaar')
        phone = data.get('phone')

        print("INPUT:", email, aadhaar, phone)

        user = User.query.filter_by(email=email, aadhaar=aadhaar, phone=phone).first()
        print("USER:", user)

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        otp = generate_otp()
        user.otp = otp
        db.session.commit()

        print("OTP GENERATED:", otp)

        # TEMP: skip email to avoid crash
        return jsonify({'success': True, 'otp': otp})

    except Exception as e:
        import traceback
        print("🔥 ERROR:", traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        aadhaar = request.form.get('aadhaar')
        phone = request.form.get('phone')
        email = request.form.get('email')

        # Check if user already exists
        user = User.query.filter((User.aadhaar == aadhaar) | (User.phone == phone) | (User.email == email)).first()
        if user:
            return render_template('register.html', message="User already exists with these details!")

        new_user = User(aadhaar=aadhaar, phone=phone, email=email)
        db.session.add(new_user)
        db.session.commit()

        return render_template('register.html', message="Registration Successful! You can now Login.")

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    entered_otp = data.get('otp')
    aadhaar = data.get('aadhaar')
    phone = data.get('phone')
    email = data.get('email')

    if not (aadhaar and phone and email and entered_otp):
         return jsonify({'success': False, 'message': 'All fields are required'}), 400

    # Verify against Database
    user = User.query.filter_by(aadhaar=aadhaar, phone=phone, email=email).first()
    
    if user and user.otp == entered_otp:
        session['user_id'] = user.id
        
        # Clear OTP after successful login
        user.otp = None 
        db.session.commit()
        
        return jsonify({'success': True, 'redirect': url_for('dashboard')})
    else:
        return jsonify({'success': False, 'message': 'Invalid Credentials or OTP'}), 401



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/contact')
def contact():
    # Allow access even without login? Assuming login required for consistency with menu
    if 'user_id' not in session:
        return redirect(url_for('home')) 
    return render_template('contact.html')

@app.route('/my-complaints')
def my_complaints():
    if 'user_id' not in session:
        return redirect(url_for('home'))
        
    user = User.query.get(session['user_id'])
    # Access complaints via relationship (reverse relation defined in model)
    # The backref in model is 'complaints', so user.complaints gives list
    return render_template('my_complaints.html', complaints=user.complaints)

# --- Admin Routes ---

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid Credentials")
            
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Calculate Statistics
    total_complaints = Complaint.query.count()
    pending_complaints = Complaint.query.filter_by(status='Pending').count()
    in_progress_complaints = Complaint.query.filter_by(status='In Progress').count()
    resolved_complaints = Complaint.query.filter_by(status='Resolved').count()
    recent_complaints = Complaint.query.order_by(Complaint.id.desc()).limit(5).all()
    
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
    
    if status_filter:
        complaints = Complaint.query.filter_by(status=status_filter).order_by(Complaint.id.desc()).all()
    else:
        complaints = Complaint.query.order_by(Complaint.id.desc()).all()
        
    return render_template('admin_complaints.html', complaints=complaints, current_filter=status_filter, active_page=active_page)

@app.route('/admin/users')
def admin_users():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users, active_page='users')

@app.route('/admin/complaint/<int:id>')
def admin_complaint_details(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    complaint = db.session.get(Complaint, id)
    if not complaint:
        abort(404)
        
    return render_template('admin_complaint_details.html', complaint=complaint, active_page='all_complaints')

@app.route('/admin/update-status/<int:id>', methods=['POST'])
def update_status(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    complaint = db.session.get(Complaint, id)
    if not complaint:
        abort(404)
        
    new_status = request.form.get('status')
    admin_comment = request.form.get('admin_comment')
    
    complaint.status = new_status
    if admin_comment:
        complaint.admin_comment = admin_comment
        
    # Create History Record
    try:
        history_entry = ComplaintHistory(
            complaint_id=complaint.id,
            status=new_status,
            comment=admin_comment
        )
        db.session.add(history_entry)
    except Exception as e:
        print(f"Error creating history: {e}")

    db.session.commit()
    
    # Send Status Update Email
    try:
        if complaint.user and complaint.user.email:
            msg = Message(f'Update on Complaint #{complaint.id}: {new_status}', recipients=[complaint.user.email])
            
            # Default Topic Image
            topic_image = TOPIC_IMAGE_MAP.get(complaint.topic, 'https://placehold.co/600x400?text=Grievance')
            
            # Check for uploaded image
            uploaded_file = request.files.get('status_image')
            has_attachment = False
            
            if uploaded_file and uploaded_file.filename != '':
                has_attachment = True
                # Read file data to attach
                file_data = uploaded_file.read()
                filename = uploaded_file.filename
                content_type = uploaded_file.content_type
                
                # Attach as inline image
                msg.attach(filename, content_type, file_data, 'inline', headers={'Content-ID': '<status_image>'})

            msg.html = render_template('email_status_update.html', 
                                     complaint=complaint,
                                     topic_image=topic_image,
                                     has_attachment=has_attachment)
            email_thread = threading.Thread(target=send_async_email, args=(app, msg))
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
