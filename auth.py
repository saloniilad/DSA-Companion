from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app import db
from models import User
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        if not username_or_email:
            flash('Username or email is required!', 'error')
            return render_template('auth/login.html')
        
        if not password:
            flash('Password is required!', 'error')
            return render_template('auth/login.html')
        
        # Check if input is email or username
        if '@' in username_or_email:
            user = User.query.filter_by(email=username_or_email).first()
        else:
            user = User.query.filter_by(username=username_or_email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember_me)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            flash(f'Welcome back, {user.get_full_name()}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username/email or password!', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not username:
            errors.append('Username is required!')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long!')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores!')
        
        if not email:
            errors.append('Email is required!')
        elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append('Please enter a valid email address!')
        
        if not password:
            errors.append('Password is required!')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters long!')
        
        if password != confirm_password:
            errors.append('Passwords do not match!')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists!')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered!')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/signup.html')
        
        try:
            # Create new user
            user = User(
                username=username,
                email=email,
                first_name=first_name if first_name else None,
                last_name=last_name if last_name else None
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('auth/signup.html')
    
    return render_template('auth/signup.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    user_name = current_user.get_full_name()
    logout_user()
    flash(f'Goodbye, {user_name}!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validation
        if not email:
            flash('Email is required!', 'error')
            return render_template('auth/edit_profile.html', user=current_user)
        
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            flash('Please enter a valid email address!', 'error')
            return render_template('auth/edit_profile.html', user=current_user)
        
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Email already registered by another user!', 'error')
            return render_template('auth/edit_profile.html', user=current_user)
        
        try:
            current_user.first_name = first_name if first_name else None
            current_user.last_name = last_name if last_name else None
            current_user.email = email
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating profile. Please try again.', 'error')
    
    return render_template('auth/edit_profile.html', user=current_user)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not current_password:
            flash('Current password is required!', 'error')
            return render_template('auth/change_password.html')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect!', 'error')
            return render_template('auth/change_password.html')
        
        if not new_password:
            flash('New password is required!', 'error')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long!', 'error')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match!', 'error')
            return render_template('auth/change_password.html')
        
        try:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while changing password. Please try again.', 'error')
    
    return render_template('auth/change_password.html')