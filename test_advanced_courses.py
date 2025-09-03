#!/usr/bin/env python3
"""
Test script to verify prerequisite display works for advanced courses
"""

import requests
import json

def test_advanced_course_recommendations():
    """Test with many completed courses to get advanced recommendations"""
    print("=== Testing Advanced Course Recommendations ===")
    
    # List of completed courses that should unlock advanced courses
    completed_courses = [
        "CS114", "CS115", "CS116", "CS280", "CS288", "CS241", "CS341",
        "MATH111", "MATH222", "MATH333", "PHYS111", "PHYS112",
        "ACCT115", "MGMT190", "FIN218", "CHEM125", "CHEM126"
    ]
    
    test_data = {
        "interests": ["algorithms", "advanced programming", "software engineering", "data structures"],
        "career_goals": "software_development",
        "difficulty_preference": "any",
        "completed_courses": completed_courses,
        "preferred_topics": ["algorithms", "advanced programming"],
        "course_ratings": {},
        "num_recommendations": 15
    }
    
    try:
        response = requests.post('http://localhost:5000/api/recommend', 
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps(test_data),
                               timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                recommendations = result['recommendations']
                print(f"API returned {len(recommendations)} recommendations")
                
                # Count courses with and without prerequisites
                with_prereqs = [r for r in recommendations if r.get('prerequisites') and r['prerequisites'] not in ['', 'None', None]]
                without_prereqs = [r for r in recommendations if not r.get('prerequisites') or r['prerequisites'] in ['', 'None', None]]
                
                print(f"Courses WITH prerequisites: {len(with_prereqs)}")
                print(f"Courses WITHOUT prerequisites: {len(without_prereqs)}")
                print()
                
                print("=== COURSES WITH PREREQUISITES ===")
                for course in with_prereqs:
                    print(f"✅ {course['id']} - {course['title']}")
                    print(f"   Prerequisites: {course['prerequisites']}")
                    print()
                
                print("=== COURSES WITHOUT PREREQUISITES ===")
                for course in without_prereqs[:5]:  # Show first 5
                    print(f"ℹ️ {course['id']} - {course['title']}")
                    print(f"   Prerequisites: {course.get('prerequisites', 'None')}")
                    print()
                    
            else:
                print(f"API error: {result.get('error')}")
        else:
            print(f"HTTP error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error: {e}")

def test_specific_courses_with_prereqs():
    """Test specific courses that should have prerequisites"""
    print("=== Testing Specific Courses with Prerequisites ===")
    
    course_ids = ["CS341", "CS356", "CS288", "ACCT325", "FIN403", "MGMT416"]
    
    try:
        response = requests.get('http://localhost:5000/api/courses', timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                all_courses = result['courses']
                
                for course_id in course_ids:
                    course = next((c for c in all_courses if c['id'] == course_id), None)
                    if course:
                        print(f"✅ {course['id']} - {course['title']}")
                        print(f"   Prerequisites: {course.get('prerequisites', 'NOT FOUND')}")
                        print()
                    else:
                        print(f"❌ Course {course_id} not found")
            else:
                print(f"API error: {result.get('error')}")
        else:
            print(f"HTTP error: {response.status_code}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_advanced_course_recommendations()
    print("\n" + "="*60 + "\n")
    test_specific_courses_with_prereqs()