from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS
import os
import secrets
from dotenv import load_dotenv
from src.recommendation_engine import RecommendationEngine
from src.data_manager import DataManager
from src.auth import AuthManager, login_required, optional_login

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure session and security
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Keep False for HTTP backend with Cloudflare
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_DOMAIN'] = None  # Don't restrict domain
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Production security headers
@app.after_request
def security_headers(response):
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Content Security Policy (basic)
    if os.getenv('FLASK_ENV') == 'production':
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
    
    return response

# Check if database exists
if not os.path.exists('data/courses.db'):
    print("Warning: data/courses.db not found. Some features may not work.")

# Initialize components
data_manager = DataManager()
recommendation_engine = RecommendationEngine(data_manager)
auth_manager = AuthManager(data_manager)

# Session permanent is set during login

@app.route('/')
def index():
    # Redirect to advisor if already logged in
    if auth_manager.is_logged_in():
        return redirect(url_for('advisor'))
    # Show landing page with login/signup options
    return render_template('landing.html')

@app.route('/advisor')
@login_required
def advisor():
    print(f"Advisor route accessed - Session: {dict(session)}")
    print(f"Is logged in: {auth_manager.is_logged_in()}")
    return render_template('index.html')

@app.route('/api/courses')
def get_courses():
    """Get all available elective courses"""
    try:
        courses = data_manager.get_all_courses()
        return jsonify({"success": True, "courses": courses})
    except Exception as e:
        print(f"Error in get_courses: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """Get course recommendations based on student input"""
    try:
        data = request.get_json()
        
        # Extract student preferences
        interests = data.get('interests', [])
        specific_topics = data.get('specific_topics', '')
        career_goals = data.get('career_goals', '')
        preferred_topics = data.get('preferred_topics', [])
        difficulty_preference = data.get('difficulty_preference', 'medium')
        completed_courses = data.get('completed_courses', [])
        num_recommendations = data.get('num_recommendations', 10)
        department_filter = data.get('department_filter', '')
        include_cross_dept = data.get('include_cross_dept', True)
        academic_level = data.get('academic_level', '')
        
        # Get recommendations
        recommendations = recommendation_engine.get_recommendations(
            interests=interests,
            specific_topics=specific_topics,
            career_goals=career_goals,
            preferred_topics=preferred_topics,
            difficulty_preference=difficulty_preference,
            completed_courses=completed_courses,
            num_recommendations=num_recommendations,
            department_filter=department_filter,
            include_cross_dept=include_cross_dept,
            academic_level=academic_level
        )
        
        return jsonify({
            "success": True, 
            "recommendations": recommendations,
            "total_count": len(recommendations)
        })
        
    except Exception as e:
        print(f"Error in get_recommendations: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/course/<course_id>')
def get_course_details(course_id):
    """Get detailed information about a specific course"""
    try:
        course = data_manager.get_course_by_id(course_id)
        if course:
            return jsonify({"success": True, "course": course})
        else:
            return jsonify({"success": False, "error": "Course not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/rate-course', methods=['POST'])
def rate_course():
    """Submit a rating for a course the student has completed"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_email', 'course_id', 'rating']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        # Validate rating
        rating = data.get('rating')
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({"success": False, "error": "Rating must be an integer between 1 and 5"}), 400
        
        # Store rating in database
        rating_data = {
            'student_email': data.get('student_email'),
            'course_id': data.get('course_id'),
            'rating': rating,
            'review': data.get('review', ''),
            'completed_semester': data.get('completed_semester', ''),
            'would_recommend': data.get('would_recommend', True)
        }
        
        # Save to database and update course average
        success = data_manager.add_student_rating(rating_data)
        
        if success:
            return jsonify({
                "success": True, 
                "message": "Rating submitted successfully!",
                "updated_average": data_manager.get_course_average_rating(data.get('course_id'))
            })
        else:
            return jsonify({"success": False, "error": "Failed to save rating"}), 500
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/course/<course_id>/ratings')
def get_course_ratings(course_id):
    """Get all ratings for a specific course"""
    try:
        ratings = data_manager.get_course_ratings(course_id)
        return jsonify({"success": True, "ratings": ratings})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/departments')
def get_departments():
    """Get all NJIT departments"""
    try:
        departments = data_manager.get_all_departments()
        return jsonify({"success": True, "departments": departments})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback on recommendations"""
    try:
        data = request.get_json()
        # Store feedback for improving recommendations
        feedback_data = {
            'student_id': data.get('student_id'),
            'recommended_courses': data.get('recommended_courses', []),
            'selected_courses': data.get('selected_courses', []),
            'rating': data.get('rating'),
            'comments': data.get('comments', '')
        }
        
        # TODO: Store feedback in database for model improvement
        return jsonify({"success": True, "message": "Feedback submitted successfully"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Authentication Routes
@app.route('/login')
def login():
    """Login page"""
    if auth_manager.is_logged_in():
        return redirect(url_for('advisor'))
    return render_template('auth/login.html')

@app.route('/register')
def register():
    """Registration page"""
    if auth_manager.is_logged_in():
        return redirect(url_for('advisor'))
    return render_template('auth/register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    """Handle user registration"""
    try:
        data = request.json
        
        # Extract form data
        email = data.get('email', '').strip()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        # Handle optional fields safely
        student_id = data.get('student_id')
        student_id = student_id.strip() if student_id else None
        
        major = data.get('major')
        major = major.strip() if major else None
        
        academic_level = data.get('academic_level') or None
        
        # Register user
        success, message, user_id = auth_manager.register_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            student_id=student_id,
            major=major,
            academic_level=academic_level
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'user_id': user_id
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle user login"""
    try:
        data = request.json
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Authenticate user
        success, message, user = auth_manager.login_user(email, password)
        
        if success:
            # Create session
            auth_manager.create_session(user)
            # Make session permanent for better persistence
            session.permanent = True
            # Force session to be saved
            session.modified = True
            
            # Debug: Print session after creation
            print(f"Login successful - Session created: {dict(session)}")
            print(f"Is logged in after creation: {auth_manager.is_logged_in()}")
            
            return jsonify({
                'success': True,
                'message': message,
                'user': user
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Handle user logout"""
    auth_manager.destroy_session()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/user')
def api_user():
    """Get current user information"""
    # Debug session data
    print(f"Session data: {dict(session)}")
    print(f"Is logged in: {auth_manager.is_logged_in()}")
    
    user = auth_manager.get_current_user()
    if user:
        return jsonify({
            'success': True,
            'user': user,
            'logged_in': True
        })
    else:
        return jsonify({
            'success': False,
            'logged_in': False
        })

# Saved Courses Routes
@app.route('/api/saved-courses')
@login_required
def api_get_saved_courses():
    """Get user's saved courses"""
    try:
        user_id = auth_manager.get_current_user_id()
        saved_courses = data_manager.get_saved_courses(user_id)
        return jsonify({
            'success': True,
            'saved_courses': saved_courses
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save-course', methods=['POST'])
@login_required
def api_save_course():
    """Save a course to user's list"""
    try:
        data = request.json
        user_id = auth_manager.get_current_user_id()
        course_id = data.get('course_id')
        notes = data.get('notes', '')
        
        if not course_id:
            return jsonify({'success': False, 'error': 'Course ID required'}), 400
        
        success = data_manager.save_course_for_user(user_id, course_id, notes)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Course saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save course'
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/remove-saved-course', methods=['POST'])
@login_required
def api_remove_saved_course():
    """Remove a course from user's saved list"""
    try:
        data = request.json
        user_id = auth_manager.get_current_user_id()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({'success': False, 'error': 'Course ID required'}), 400
        
        success = data_manager.remove_saved_course(user_id, course_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Course removed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to remove course'
            }), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/saved-courses')
@login_required
def saved_courses_page():
    """Saved courses page"""
    return render_template('saved_courses.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
else:
    # For production deployment (Railway, Heroku, etc.)
    # Initialize components only when needed, not on import
    pass
