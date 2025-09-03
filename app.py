from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
from src.recommendation_engine import RecommendationEngine
from src.data_manager import DataManager

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize components
data_manager = DataManager()
recommendation_engine = RecommendationEngine(data_manager)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/courses')
def get_courses():
    """Get all available elective courses"""
    try:
        courses = data_manager.get_all_courses()
        return jsonify({"success": True, "courses": courses})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """Get course recommendations based on student input"""
    try:
        data = request.get_json()
        
        # Extract student preferences
        interests = data.get('interests', [])
        career_goals = data.get('career_goals', '')
        preferred_topics = data.get('preferred_topics', [])
        difficulty_preference = data.get('difficulty_preference', 'medium')
        completed_courses = data.get('completed_courses', [])
        num_recommendations = data.get('num_recommendations', 10)
        department_filter = data.get('department_filter', '')
        academic_level = data.get('academic_level', '')
        
        # Get recommendations
        recommendations = recommendation_engine.get_recommendations(
            interests=interests,
            career_goals=career_goals,
            preferred_topics=preferred_topics,
            difficulty_preference=difficulty_preference,
            completed_courses=completed_courses,
            num_recommendations=num_recommendations,
            department_filter=department_filter,
            academic_level=academic_level
        )
        
        return jsonify({
            "success": True, 
            "recommendations": recommendations,
            "total_count": len(recommendations)
        })
        
    except Exception as e:
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)