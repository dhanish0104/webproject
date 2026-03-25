from app import app, db, Complaint, User

with app.app_context():
    resolved = Complaint.query.filter_by(status='Resolved').all()
    print(f"Total Resolved in DB: {len(resolved)}")
    for r in resolved:
        print(f"ID: {r.id}, Topic: {r.topic}, User ID: {r.user_id}, Admin Comment: {r.admin_comment}")
    
    # Check current session user if possible (we can't easily, but we can check the custom user)
    user = User.query.filter_by(email="dhanishkanth1122@gmail.com").first()
    if user:
        user_resolved = Complaint.query.filter_by(user_id=user.id, status='Resolved').all()
        print(f"User {user.email} resolved count: {len(user_resolved)}")
