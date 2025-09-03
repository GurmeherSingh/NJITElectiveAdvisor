#!/usr/bin/env python3
"""
Demo: NJIT Student Rating System
Shows how the new rating system works
"""

from src.data_manager import DataManager
import json

def demo_rating_system():
    print("🎓 NJIT Student Rating System Demo")
    print("=" * 50)
    
    # Initialize data manager
    dm = DataManager()
    
    print("1. 📊 Current Course Statistics:")
    stats = dm.get_course_statistics()
    print(f"   Total Courses: {stats['total_courses']}")
    print(f"   Departments: {', '.join(stats['departments'].keys())}")
    print()
    
    print("2. 🌟 Simulating Student Ratings:")
    
    # Simulate some student ratings
    sample_ratings = [
        {
            'student_email': 'student1@njit.edu',
            'course_id': 'CS480',
            'rating': 5,
            'review': 'Excellent course! Really enjoyed learning about ML algorithms.',
            'completed_semester': 'Fall 2024',
            'would_recommend': True
        },
        {
            'student_email': 'student2@njit.edu', 
            'course_id': 'CS480',
            'rating': 4,
            'review': 'Good course but quite challenging. Worth the effort!',
            'completed_semester': 'Fall 2024',
            'would_recommend': True
        },
        {
            'student_email': 'student3@njit.edu',
            'course_id': 'CS485',
            'rating': 5,
            'review': 'Love cybersecurity! This course opened my eyes to the field.',
            'completed_semester': 'Spring 2024',
            'would_recommend': True
        },
        {
            'student_email': 'student4@njit.edu',
            'course_id': 'CS490',
            'rating': 4,
            'review': 'Great capstone experience. Learned a lot about teamwork.',
            'completed_semester': 'Spring 2024',
            'would_recommend': True
        }
    ]
    
    for rating in sample_ratings:
        success = dm.add_student_rating(rating)
        if success:
            print(f"   ✅ Added rating for {rating['course_id']} by {rating['student_email']}")
        else:
            print(f"   ❌ Failed to add rating for {rating['course_id']}")
    
    print()
    print("3. 📈 Updated Course Ratings:")
    
    # Show updated ratings
    for course_id in ['CS480', 'CS485', 'CS490']:
        avg_rating = dm.get_course_average_rating(course_id)
        ratings = dm.get_course_ratings(course_id)
        print(f"   {course_id}: {avg_rating:.1f}/5.0 ({len(ratings)} ratings)")
        
        if ratings:
            for rating in ratings[:2]:  # Show first 2 reviews
                print(f"      • {rating['rating']}/5 - \"{rating['review'][:50]}...\"")
    
    print()
    print("4. 🏢 Available Departments:")
    departments = dm.get_all_departments()
    for dept in departments[:5]:  # Show first 5
        print(f"   • {dept['name']} ({dept['code']}) - {dept['college']}")
    
    print()
    print("5. 📝 Department Templates Created:")
    import os
    if os.path.exists("data/departments"):
        templates = os.listdir("data/departments")
        for template in templates[:5]:  # Show first 5
            print(f"   • {template}")
    
    print()
    print("✅ Demo Complete!")
    print()
    print("🎯 What students can now do:")
    print("• Rate courses they've completed (1-5 stars)")
    print("• Write detailed reviews")
    print("• See real student ratings in recommendations")
    print("• Browse electives from ALL NJIT departments")
    print()
    print("🔗 API Endpoints Available:")
    print("• POST /api/rate-course - Submit course rating")
    print("• GET /api/course/<id>/ratings - Get course ratings")
    print("• GET /api/departments - Get all departments")
    print("• GET /api/courses - Get all courses")
    print("• POST /api/recommend - Get personalized recommendations")

if __name__ == "__main__":
    demo_rating_system()