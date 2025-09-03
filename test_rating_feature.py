#!/usr/bin/env python3
"""
Test script for the new course rating feature
"""

import requests
import json

def test_rating_endpoint():
    """Test the new /api/rate-course endpoint"""
    
    # Test data
    rating_data = {
        "course_id": "CS280",
        "rating": 4,
        "student_email": "test_user@njit.edu"
    }
    
    try:
        # Test the rating endpoint
        response = requests.post('http://localhost:5000/api/rate-course', 
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps(rating_data))
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Rating endpoint test passed!")
            print(f"Response: {result}")
        else:
            print(f"❌ Rating endpoint test failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the app is running with: python app.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_recommendation_endpoint():
    """Test the recommendation endpoint without difficulty preference"""
    
    # Test data
    recommendation_data = {
        "interests": ["artificial intelligence", "machine learning"],
        "career_goals": "software_development",
        "difficulty_preference": "any",
        "completed_courses": ["CS280", "CS288"],
        "preferred_topics": ["artificial intelligence", "machine learning"],
        "course_ratings": {"CS280": 4, "CS288": 5}
    }
    
    try:
        # Test the recommendation endpoint
        response = requests.post('http://localhost:5000/api/recommend', 
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps(recommendation_data))
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Recommendation endpoint test passed!")
            print(f"Found {result.get('total_count', 0)} recommendations")
        else:
            print(f"❌ Recommendation endpoint test failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the app is running with: python app.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    print("=== Testing New Course Rating Feature ===\n")
    
    print("1. Testing course rating endpoint...")
    test_rating_endpoint()
    
    print("\n2. Testing recommendation endpoint...")
    test_recommendation_endpoint()
    
    print("\n=== Test Complete ===")