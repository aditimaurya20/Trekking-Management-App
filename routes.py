from flask import render_template, request, redirect, url_for, flash, session
from app import app
from datetime import datetime
from models import db, User, Trek, Booking, StaffProfile

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated!', 'danger')
                return redirect(url_for('login'))
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'staff':
                return redirect(url_for('staff_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists!', 'danger')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            role='trekker',
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Get ID first
        user.generate_custom_id()  
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='trekker').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    
    return render_template('admin/dashboard.html',
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings)

@app.route('/admin/treks')
def admin_treks():
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    search = request.args.get('search', '')
    if search:
        treks = Trek.query.filter(
            (Trek.name.contains(search)) |
            (Trek.custom_id.contains(search))
        ).all()
    else:
        treks = Trek.query.all()
    staff_list = User.query.filter_by(role='staff').all()
    staff_dict = {s.id: s.username for s in staff_list}
    return render_template('admin/manage_treks.html', treks=treks, search=search, staff_dict=staff_dict)

@app.route('/admin/treks/add', methods=['GET', 'POST'])
def admin_add_trek():
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    staff_list = User.query.filter_by(role='staff').all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = request.form.get('duration')
        available_slots = request.form.get('available_slots')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        staff_id = request.form.get('staff_id') or None

        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=int(duration),
            available_slots=int(available_slots),
            start_date=start_date,
            end_date=end_date,
            staff_id=staff_id,
            status='Pending'
        )
        db.session.add(trek)
        db.session.flush()  # Get ID first
        trek.generate_custom_id()  # Generate T10001
        db.session.commit()
        flash('Trek added successfully!', 'success')
        return redirect(url_for('admin_treks'))
    
    return render_template('admin/add_trek.html', staff_list=staff_list)


@app.route('/admin/treks/edit/<int:trek_id>', methods=['GET', 'POST'])
def admin_edit_trek(trek_id):
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    trek = Trek.query.get_or_404(trek_id)
    staff_list = User.query.filter_by(role='staff').all()
    
    if request.method == 'POST':
        trek.name = request.form.get('name')
        trek.location = request.form.get('location')
        trek.difficulty = request.form.get('difficulty')
        trek.duration = int(request.form.get('duration'))
        trek.available_slots = int(request.form.get('available_slots'))
        trek.start_date = request.form.get('start_date')
        trek.end_date = request.form.get('end_date')
        trek.status = request.form.get('status')
        trek.staff_id = request.form.get('staff_id') or None
        
        db.session.commit()
        flash('Trek updated successfully!', 'success')
        return redirect(url_for('admin_treks'))
    
    return render_template('admin/edit_trek.html', trek=trek, staff_list=staff_list)


@app.route('/admin/treks/delete/<int:trek_id>')
def admin_delete_trek(trek_id):
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    flash('Trek deleted successfully!', 'success')
    return redirect(url_for('admin_treks'))

@app.route('/admin/staff')
def admin_staff():
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    search = request.args.get('search', '')
    if search:
        staff_list = User.query.filter(
            User.role == 'staff',
            (User.username.contains(search)) |
            (User.custom_id.contains(search))
        ).all()
    else:
        staff_list = User.query.filter_by(role='staff').all()
    
    return render_template('admin/manage_staff.html', staff_list=staff_list, search=search)


@app.route('/admin/staff/add', methods=['GET', 'POST'])
def admin_add_staff():
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        contact = request.form.get('contact')

        existing = User.query.filter_by(username=username).first()
        if existing:
            flash('Username already exists!', 'danger')
            return redirect(url_for('admin_add_staff'))

        staff = User(
            username=username,
            email=email,
            role='staff',
            is_active=True
        )
        staff.set_password(password)
        db.session.add(staff)
        db.session.flush()  # Get ID first
        staff.generate_custom_id()  # Generate S10001

        profile = StaffProfile(
            user_id=staff.id,
            name=username,
            contact=contact,
            status='Active'
        )
        db.session.add(profile)
        db.session.commit()

        flash('Staff added successfully!', 'success')
        return redirect(url_for('admin_staff'))
    
    return render_template('admin/add_staff.html')


@app.route('/admin/staff/blacklist/<int:staff_id>')
def admin_blacklist_staff(staff_id):
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    staff = User.query.get_or_404(staff_id)
    staff.is_active = False
    db.session.commit()
    flash('Staff blacklisted!', 'warning')
    return redirect(url_for('admin_staff'))


@app.route('/admin/staff/activate/<int:staff_id>')
def admin_activate_staff(staff_id):
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    staff = User.query.get_or_404(staff_id)
    staff.is_active = True
    db.session.commit()
    flash('Staff activated!', 'success')
    return redirect(url_for('admin_staff'))


@app.route('/admin/staff/delete/<int:staff_id>')
def admin_delete_staff(staff_id):
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    staff = User.query.get_or_404(staff_id)
    db.session.delete(staff)
    db.session.commit()
    flash('Staff deleted!', 'success')
    return redirect(url_for('admin_staff'))

@app.route('/admin/users')  # Admin - View all users
def admin_users():
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    search = request.args.get('search', '')
    if search:
        users = User.query.filter(
            User.role == 'trekker',
            (User.username.contains(search)) |
            (User.custom_id.contains(search))
        ).all()
    else:
        users = User.query.filter_by(role='trekker').all()
    
    return render_template('admin/manage_users.html', users=users, search=search)


@app.route('/admin/users/blacklist/<int:user_id>')  # Admin - Blacklist a user
def admin_blacklist_user(user_id):
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    flash('User blacklisted!', 'warning')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/activate/<int:user_id>')  # Admin - Activate a user
def admin_activate_user(user_id):
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash('User activated!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/bookings')  # Admin - View all bookings
def admin_bookings():
    if session.get('role') != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    bookings = Booking.query.all()
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/staff/dashboard') 
def staff_dashboard():
    if session.get('role') != 'staff':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    treks = Trek.query.filter_by(staff_id=session.get('user_id')).all()
    
    return render_template('staff/dashboard.html', treks=treks)


@app.route('/staff/trek/<int:trek_id>')  # Staff - View trek details
def staff_trek_detail(trek_id):
    if session.get('role') != 'staff':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    trek = Trek.query.get_or_404(trek_id)
    
    # Make sure only assigned staff can access
    if trek.staff_id != session.get('user_id'):
        flash('You are not assigned to this trek!', 'danger')
        return redirect(url_for('staff_dashboard'))
    
    return render_template('staff/trek_detail.html', trek=trek)


@app.route('/staff/trek/<int:trek_id>/update', methods=['POST'])  # Staff - Update trek
def staff_update_trek(trek_id):
    if session.get('role') != 'staff':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    trek = Trek.query.get_or_404(trek_id)
    
    # Make sure only assigned staff can update
    if trek.staff_id != session.get('user_id'):
        flash('You are not assigned to this trek!', 'danger')
        return redirect(url_for('staff_dashboard'))
    
    trek.available_slots = int(request.form.get('available_slots'))
    trek.status = request.form.get('status')
    db.session.commit()
    
    flash('Trek updated successfully!', 'success')
    return redirect(url_for('staff_trek_detail', trek_id=trek_id))


@app.route('/staff/trek/<int:trek_id>/participants')  # Staff - View participants
def staff_participants(trek_id):
    if session.get('role') != 'staff':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    trek = Trek.query.get_or_404(trek_id)
    
    # Make sure only assigned staff can view
    if trek.staff_id != session.get('user_id'):
        flash('You are not assigned to this trek!', 'danger')
        return redirect(url_for('staff_dashboard'))
    
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    
    return render_template('staff/participants.html', trek=trek, bookings=bookings)

# ─── USER ROUTES ───────────────────────────────

@app.route('/user/dashboard')  # User - View available treks
def user_dashboard():
    if session.get('role') != 'trekker':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    search = request.args.get('search', '')
    difficulty = request.args.get('difficulty', '')
    
    # Get only open treks
    query = Trek.query.filter_by(status='Open')
    
    if search:
        query = query.filter(
            (Trek.name.contains(search)) | 
            (Trek.location.contains(search))
        )
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    treks = query.all()
    
    # Get user booking stats
    user_id = session.get('user_id')
    total_booked = Booking.query.filter_by(user_id=user_id, status='Booked').count()
    total_completed = Booking.query.filter_by(user_id=user_id, status='Completed').count()
    total_cancelled = Booking.query.filter_by(user_id=user_id, status='Cancelled').count()
    
    return render_template('user/dashboard.html',
        treks=treks,
        search=search,
        difficulty=difficulty,
        total_booked=total_booked,
        total_completed=total_completed,
        total_cancelled=total_cancelled)


@app.route('/user/book/<int:trek_id>')  # User - Book a trek
def user_book_trek(trek_id):
    if session.get('role') != 'trekker':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    trek = Trek.query.get_or_404(trek_id)
    user_id = session.get('user_id')
    
    if trek.status != 'Open':
        flash('This trek is not open for booking!', 'danger')
        return redirect(url_for('user_dashboard'))
    
    if trek.available_slots <= 0:
        flash('No slots available for this trek!', 'danger')
        return redirect(url_for('user_dashboard'))
    
    existing = Booking.query.filter_by(
        user_id=user_id, 
        trek_id=trek_id,
        status='Booked'
    ).first()
    if existing:
        flash('You have already booked this trek!', 'danger')
        return redirect(url_for('user_dashboard'))
    
    # Create booking
    booking = Booking(
        user_id=user_id,
        trek_id=trek_id,
        booking_date=datetime.now().strftime('%Y-%m-%d'),
        status='Booked'
    )
    db.session.add(booking)
    db.session.flush()  # Get ID first
    booking.generate_custom_id()  # Generate B10001
    
    trek.available_slots -= 1     # Reduce available slots
    db.session.commit()
    
    flash('Trek booked successfully!', 'success')
    return redirect(url_for('user_my_bookings'))


@app.route('/user/my-bookings')  # User - View my bookings
def user_my_bookings():
    if session.get('role') != 'trekker':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    bookings = Booking.query.filter_by(
        user_id=session.get('user_id')
    ).all()
    
    return render_template('user/my_bookings.html', bookings=bookings)


@app.route('/user/cancel/<int:booking_id>')  # User - Cancel a booking
def user_cancel_booking(booking_id):
    if session.get('role') != 'trekker':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != session.get('user_id'):   # This will make sure user can only cancel their own booking
        flash('Access denied!', 'danger')
        return redirect(url_for('user_my_bookings'))
    
    booking.status = 'Cancelled'
    booking.trek.available_slots += 1  # Return slot
    db.session.commit()
    
    flash('Booking cancelled successfully!', 'success')
    return redirect(url_for('user_my_bookings'))


@app.route('/user/profile', methods=['GET', 'POST'])  # User - View/Edit profile
def user_profile():
    if session.get('role') != 'trekker':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(session.get('user_id'))
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        password = request.form.get('password')
        if password:
            user.set_password(password)
        db.session.commit()
        session['username'] = user.username
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_profile'))
    
    return render_template('user/profile.html', user=user)