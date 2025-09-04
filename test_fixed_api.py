#!/usr/bin/env python3
"""
Test the fixed API with STS department
"""

import json
import requests

def test_sts_department():
    """Test API call with STS department"""
    print("🧪 Testing API with STS department...")
    
    test_data = {
        'interests': ['artificial intelligence machine learning'],
        'specific_topics': '',
        'career_goals': 'ai_ml',
        'difficulty_preference': 'any',
        'completed_courses': [],
        'preferred_topics': ['artificial intelligence machine learning'],
        'course_ratings': {},
        'num_recommendations': 5,
        'department_filter': 'Science Technology Society',
        'academic_level': 'junior'
    }
    
    try:
        response = requests.post('http://localhost:5000/api/recommend',
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps(test_data),
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f'✅ API working! Found {result.get("total_count", 0)} STS courses')
            
            for i, course in enumerate(result.get('recommendations', [])[:3], 1):
                print(f'   {i}. {course["id"]} - {course["title"]}')
                
        else:
            print(f'❌ HTTP Error: {response.status_code}')
            print(response.text)
            
    except Exception as e:
        print(f'❌ Error: {e}')

def test_computer_science():
    """Test API call with Computer Science department"""
    print("\n🧪 Testing API with Computer Science department...")
    
    test_data = {
        'interests': ['artificial intelligence machine learning'],
        'specific_topics': '',
        'career_goals': 'ai_ml',
        'difficulty_preference': 'any',
        'completed_courses': [],
        'preferred_topics': ['artificial intelligence machine learning'],
        'course_ratings': {},
        'num_recommendations': 5,
        'department_filter': 'Computer Science',
        'academic_level': 'junior'
    }
    
    try:
        response = requests.post('http://localhost:5000/api/recommend',
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps(test_data),
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f'✅ API working! Found {result.get("total_count", 0)} CS courses')
            
            for i, course in enumerate(result.get('recommendations', [])[:3], 1):
                print(f'   {i}. {course["id"]} - {course["title"]}')
                
        else:
            print(f'❌ HTTP Error: {response.status_code}')
            print(response.text)
            
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    test_sts_department()
    test_computer_science()