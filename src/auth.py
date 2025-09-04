"""
Authentication module for NJIT Elective Advisor
Handles user registration, login, password hashing, and session management
"""

import hashlib
import secrets
import re
from typing import Optional, Dict, Tuple
from functools import wraps
from flask import session, request, jsonify, redirect, url_for

class AuthManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.session_timeout = 3600  # 1 hour in seconds
    
    def hash_password(self, password: str) -> str:
        """Create a secure hash of the password"""
        # Generate a random salt
        salt = secrets.token_hex(32)
        # Create hash with salt
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        # Store salt and hash together
        return salt + pwd_hash.hex()
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify a password against its hash"""
        try:
            # Extract salt (first 64 characters)
            salt = stored_hash[:64]
            # Extract hash (rest of the string)
            stored_pwd_hash = stored_hash[64:]
            # Hash the provided password with the same salt
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            # Compare hashes
            return pwd_hash.hex() == stored_pwd_hash
        except:
            return False
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    def register_user(self, email: str, password: str, first_name: str, last_name: str,
                     student_id: Optional[str] = None, major: Optional[str] = None,
                     academic_level: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
        """Register a new user"""
        
        # Validate email
        if not self.validate_email(email):
            return False, "Invalid email format", None
        
        # Check if email already exists
        if self.data_manager.get_user_by_email(email):
            return False, "Email already registered", None
        
        # Validate password
        is_valid, message = self.validate_password(password)
        if not is_valid:
            return False, message, None
        
        # Validate required fields
        if not first_name.strip() or not last_name.strip():
            return False, "First name and last name are required", None
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Create user
        user_id = self.data_manager.create_user(
            email=email.lower().strip(),
            password_hash=password_hash,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            student_id=student_id.strip() if student_id and student_id.strip() else None,
            major=major.strip() if major and major.strip() else None,
            academic_level=academic_level
        )
        
        if user_id:
            return True, "Account created successfully", user_id
        else:
            return False, "Failed to create account", None
    
    def login_user(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Authenticate user login"""
        
        # Validate email format
        if not self.validate_email(email):
            return False, "Invalid email format", None
        
        # Get user from database
        user = self.data_manager.get_user_by_email(email.lower().strip())
        if not user:
            return False, "Invalid email or password", None
        
        # Verify password
        if not self.verify_password(password, user['password_hash']):
            return False, "Invalid email or password", None
        
        # Update last login
        self.data_manager.update_last_login(user['id'])
        
        # Remove sensitive data before returning
        safe_user = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return True, "Login successful", safe_user
    
    def create_session(self, user: Dict) -> None:
        """Create user session"""
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['user_name'] = f"{user['first_name']} {user['last_name']}"
        session['logged_in'] = True
    
    def destroy_session(self) -> None:
        """Destroy user session"""
        session.clear()
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return session.get('logged_in', False) and session.get('user_id') is not None
    
    def get_current_user_id(self) -> Optional[int]:
        """Get current user ID from session"""
        return session.get('user_id') if self.is_logged_in() else None
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current user data"""
        if not self.is_logged_in():
            return None
        
        user_id = session.get('user_id')
        return self.data_manager.get_user_by_id(user_id)


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in using session data
        logged_in = session.get('logged_in', False)
        user_id = session.get('user_id')
        
        if not logged_in or user_id is None:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def optional_login(f):
    """Decorator for routes that work with or without login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This decorator doesn't enforce login but makes user data available
        return f(*args, **kwargs)
    return decorated_function