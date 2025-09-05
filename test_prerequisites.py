#!/usr/bin/env python3
"""
Test script to check prerequisites in the API response
"""

import requests
import json
from src.data_manager import DataManager

def test_database_directly():
    """Test prerequisites directly from database"""
    print("=== Testing Database Directly ===")
    
    data_manager = DataManager()
    courses = data_manager.get_all_courses()
    
    # Check a few courses with prerequisites
    courses_with_prereqs = [c for c in courses if c.get('prerequisites') and c['prerequisites'] not in ['', 'None']][:5]
    
    print(f"Found {len(courses_with_prereqs)} courses with prerequisites")
    for course in courses_with_prereqs:
        print(f"Course: {course['id']} - {course['title']}")
        print(f"Prerequisites: {course['prerequisites']}")
        print("---")
    
    # SOPHOMORE FILTER: Check sophomore-level courses
    print("\n=== SOPHOMORE FILTER TEST ===")
    sophomore_courses = [c for c in courses if c.get('level', '').lower() == 'sophomore'][:10]
    print(f"Found {len(sophomore_courses)} sophomore-level courses")
    for course in sophomore_courses:
        print(f"Course: {course['id']} - {course['title']} (Level: {course.get('level', 'N/A')})")
        print(f"Prerequisites: {course.get('prerequisites', 'None')}")
        print("---")

def test_api_response():
    """Test prerequisites in API response"""
    print("\n=== Testing API Response ===")
    
    test_data = {
        "interests": ["computer science"],
        "career_goals": "software_development",
        "difficulty_preference": "any",
        "completed_courses": [],
        "preferred_topics": ["programming"],
        "course_ratings": {},
        "num_recommendations": 5,
        "academic_level": "Sophomore"  # SOPHOMORE FILTER
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
                for course in result['recommendations'][:3]:
                    print(f"Course: {course['id']} - {course['title']}")
                    print(f"Prerequisites: {course.get('prerequisites', 'NOT FOUND')}")
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

if __name__ == "__main__":
    test_database_directly()
    test_api_response()