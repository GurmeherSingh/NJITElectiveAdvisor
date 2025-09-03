#!/usr/bin/env python3
"""
Test script to check specific courses with prerequisites
"""

import requests
import json

def test_api_with_completed_courses():
    """Test API with completed courses to get advanced recommendations"""
    print("=== Testing API with Completed Courses ===")
    
    test_data = {
        "interests": ["programming", "software engineering"],
        "career_goals": "software_development",
        "difficulty_preference": "any",
        "completed_courses": ["CS114", "CS115", "CS280", "CS241"],  # Prerequisites for advanced courses
        "preferred_topics": ["programming", "algorithms"],
        "course_ratings": {},
        "num_recommendations": 10
    }
    
    try:
        response = requests.post('http://localhost:5000/api/recommend', 
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps(test_data),
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"API returned {len(result['recommendations'])} recommendations")
                for course in result['recommendations']:
                    prereqs = course.get('prerequisites', 'NOT FOUND')
                    print(f"Course: {course['id']} - {course['title']}")
                    print(f"Prerequisites: {prereqs}")
                    print(f"Department: {course.get('department', 'Unknown')}")
                    print("---")
            else:
                print(f"API error: {result.get('error')}")
        else:
            print(f"HTTP error: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Make sure app is running.")
    except Exception as e:
        print(f"Error: {e}")

def test_courses_endpoint():
    """Test the /api/courses endpoint directly"""
    print("\n=== Testing /api/courses Endpoint ===")
    
    try:
        response = requests.get('http://localhost:5000/api/courses', timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                courses = result['courses']
                # Find courses with prerequisites
                courses_with_prereqs = [c for c in courses if c.get('prerequisites') and c['prerequisites'] not in ['', 'None', None]]
                
                print(f"Total courses: {len(courses)}")
                print(f"Courses with prerequisites: {len(courses_with_prereqs)}")
                
                # Show a few examples
                for course in courses_with_prereqs[:5]:
                    print(f"Course: {course['id']} - {course['title']}")
                    print(f"Prerequisites: {course['prerequisites']}")
                    print("---")
            else:
                print(f"API error: {result.get('error')}")
        else:
            print(f"HTTP error: {response.status_code}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_with_completed_courses()
    test_courses_endpoint()