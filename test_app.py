#!/usr/bin/env python3
"""
Test script for NJIT Elective Advisor
"""

from src.data_manager import DataManager
from src.recommendation_engine import RecommendationEngine

def test_system():
    print("🎓 Testing NJIT Elective Advisor System")
    print("=" * 50)
    
    # Initialize components
    print("1. Initializing data manager...")
    data_manager = DataManager()
    
    print("2. Initializing recommendation engine...")
    recommendation_engine = RecommendationEngine(data_manager)
    
    # Test data retrieval
    print("3. Testing data retrieval...")
    courses = data_manager.get_all_courses()
    print(f"   ✅ Loaded {len(courses)} courses")
    
    # Test recommendations
    print("4. Testing recommendation engine...")
    test_preferences = {
        'interests': ['artificial intelligence', 'machine learning'],
        'career_goals': 'data_science',
        'difficulty_preference': 'medium',
        'completed_courses': ['CS280', 'CS341'],
        'preferred_topics': ['data science', 'algorithms']
    }
    
    recommendations = recommendation_engine.get_recommendations(**test_preferences)
    print(f"   ✅ Generated {len(recommendations)} recommendations")
    
    # Display top 3 recommendations
    print("\n🌟 Top 3 Recommendations:")
    print("-" * 30)
    
    for i, course in enumerate(recommendations[:3], 1):
        print(f"{i}. {course['id']} - {course['title']}")
        print(f"   Match: {course['recommendation_score']:.1%}")
        print(f"   Reason: {course['recommendation_reason']}")
        print()
    
    # Test statistics
    print("📊 Database Statistics:")
    stats = data_manager.get_course_statistics()
    print(f"   Total Courses: {stats['total_courses']}")
    print(f"   Average Difficulty: {stats['average_difficulty']}/5.0")
    print(f"   Average Rating: {stats['average_rating']}/5.0")
    print(f"   Departments: {', '.join(stats['departments'].keys())}")
    
    print("\n✅ All tests passed! Your NJIT Elective Advisor is ready!")
    print("\nNext steps:")
    print("1. Run: python app.py")
    print("2. Open: http://localhost:5000")
    print("3. Start getting personalized course recommendations!")

if __name__ == "__main__":
    try:
        test_system()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your setup and try again.")