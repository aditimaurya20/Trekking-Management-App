from app import app  # Import Flask app
from models import db, User  # Import database and User model

with app.app_context():
    db.create_all()  # Create all tables
    
    # Check if admin already exists
    admin = User.query.filter_by(role='admin').first()
    
    if not admin:
        admin = User(
            username='admin',
            email='admin@trekking.com',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()  # Get ID before commit
        admin.generate_custom_id()  # Generate A10001
        db.session.commit()
        print(f"Admin created! ID: {admin.custom_id}")
    else:
        print("Admin already exists!")