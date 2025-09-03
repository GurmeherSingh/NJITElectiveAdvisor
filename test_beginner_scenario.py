#!/usr/bin/env python3
"""
Test beginner scenario to see if courses with prerequisites now appear
"""

import requests
import json

def test_beginner_recommendations():
    """Test with no completed courses to see if courses with prerequisites appear"""
    print("=== Testing Beginner Recommendations (No Completed Courses) ===")
    
    test_data = {
        "interests": ["programming", "computer science"],
        "career_goals": "software_development",
        "difficulty_preference": "any",
        "completed_courses": [],  # No completed courses
        "preferred_topics": ["programming"],
        "course_ratings": {},
        "num_recommendations": 20
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
                
                # Categorize courses
                with_course_prereqs = []
                with_standing_prereqs = []
                no_prereqs = []
                
                for course in recommendations:
                    prereqs = course.get('prerequisites', '')
                    if not prereqs or prereqs in ['', 'None', None]:
                        no_prereqs.append(course)
                    elif any(prereq in prereqs for prereq in ['Junior', 'Senior', 'standing', 'majors', 'restriction']):
                        with_standing_prereqs.append(course)
                    else:
                        with_course_prereqs.append(course)
                
                print(f"\n📊 BREAKDOWN:")
                print(f"Courses with ACTUAL course prerequisites: {len(with_course_prereqs)}")
                print(f"Courses with standing/restriction prerequisites: {len(with_standing_prereqs)}")
                print(f"Courses with NO prerequisites: {len(no_prereqs)}")
                
                print(f"\n✅ COURSES WITH ACTUAL COURSE PREREQUISITES:")
                for course in with_course_prereqs:
                    print(f"  {course['id']} - {course['title']}")
                    print(f"     Prerequisites: {course['prerequisites']}")
                    print(f"     Match: {course.get('recommendation_score', 0)*100:.0f}%")
                    print()
                    
                print(f"\n📋 COURSES WITH STANDING PREREQUISITES:")
                for course in with_standing_prereqs[:3]:  # Show first 3
                    print(f"  {course['id']} - {course['title']}")
                    print(f"     Prerequisites: {course['prerequisites']}")
                    
            else:
                print(f"API error: {result.get('error')}")
        else:
            print(f"HTTP error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_beginner_recommendations()