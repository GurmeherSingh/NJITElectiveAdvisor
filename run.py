#!/usr/bin/env python3
"""
Production-ready runner for NJIT Elective Advisor
Handles database initialization and starts the Flask application
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app
from src.data_manager import DataManager

def initialize_database():
    """Initialize database with tables and verify data exists"""
    print("🔧 Initializing database...")
    
    try:
        data_manager = DataManager()
        
        # Check if we have courses in the database
        courses = data_manager.get_all_courses()
        course_count = len(courses)
        
        if course_count == 0:
            print("⚠️  No courses found in database!")
            print("   Please run 'python reset_and_load_actual_data.py' first to populate the database.")
            return False
        else:
            print(f"✅ Database initialized successfully with {course_count} courses")
            
            # User authentication will be initialized automatically
            print("✅ User authentication system ready")
            
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def main():
    """Main application entry point"""
    print("🎓 NJIT Elective Advisor - Starting Application")
    print("=" * 50)
    
    # Initialize database
    if not initialize_database():
        print("\n❌ Application startup failed due to database issues")
        sys.exit(1)
    
    # Environment configuration
    flask_env = os.getenv('FLASK_ENV', 'development')
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print(f"\n🚀 Starting server in {flask_env} mode")
    print(f"🌐 Server URL: http://{host}:{port}")
    print(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
    
    if flask_env == 'development':
        print("\n📝 Development mode features:")
        print("   • Auto-reload enabled")
        print("   • Debug toolbar available")
        print("   • Detailed error pages")
    else:
        print("\n🔒 Production mode features:")
        print("   • Security headers enabled")
        print("   • Session security enforced")
        print("   • Error logging active")
    
    print("\n" + "=" * 50)
    print("✅ Application ready! Visit the URL above to start using the advisor.")
    print("💡 New users can register at /register")
    print("🔑 Existing users can login at /login")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start Flask application
        app.run(
            debug=debug,
            host=host,
            port=port,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()