#!/usr/bin/env python3
"""
Test final course ranking after fixes
"""

import requests
import json

def test_beginner_cs_recommendations():
    """Test CS recommendations for a complete beginner"""
    print("=== CS Recommendations for Complete Beginner ===")
    
    test_data = {
        "interests": ["programming", "computer science"],
        "career_goals": "software_development",
        "difficulty_preference": "any",
        "completed_courses": [],  # Complete beginner
        "preferred_topics": ["programming"],
        "course_ratings": {},
        "num_recommendations": 15,
        "department_filter": "Computer Science"
    }
    
    try:
        response = requests.post('http://localhost:5000/api/recommend', 
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps(test_data),
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                recommendations = result['recommendations']
                print(f"Found {len(recommendations)} CS recommendations\n")
                
                print("🏆 TOP 10 RECOMMENDED COURSES:")
                for i, course in enumerate(recommendations[:10], 1):
                    level = course.get('level', 'Unknown')
                    prereqs = course.get('prerequisites', 'None')
                    if prereqs and len(prereqs) > 40:
                        prereqs = prereqs[:37] + "..."
                    
                    match_score = course.get('recommendation_score', 0) * 100
                    
                    # Identify course type for display
                    if "senior" in level.lower():
                        level_icon = "🔴"
                    elif "junior" in level.lower():
                        level_icon = "🟡"
                    elif "sophomore" in level.lower():
                        level_icon = "🔵"
                    elif "freshman" in level.lower():
                        level_icon = "🟢"
                    else:
                        level_icon = "⚪"
                    
                    print(f"{i:2}. {level_icon} {course['id']} - {course['title']}")
                    print(f"     Level: {level} | Match: {match_score:.1f}%")
                    if prereqs and prereqs != 'None':
                        print(f"     Prerequisites: {prereqs}")
                    print()
                
                # Analyze the ranking
                senior_courses = [c for c in recommendations if 'senior' in c.get('level', '').lower()]
                freshman_courses = [c for c in recommendations if 'freshman' in c.get('level', '').lower()]
                
                print("📊 RANKING ANALYSIS:")
                print(f"   Senior courses found: {len(senior_courses)}")
                print(f"   Freshman courses found: {len(freshman_courses)}")
                
                if senior_courses:
                    senior_positions = [i+1 for i, c in enumerate(recommendations) if 'senior' in c.get('level', '').lower()]
                    print(f"   Senior courses ranked at positions: {senior_positions[:3]}")
                
                if freshman_courses:
                    freshman_positions = [i+1 for i, c in enumerate(recommendations) if 'freshman' in c.get('level', '').lower()]
                    print(f"   Freshman courses ranked at positions: {freshman_positions[:3]}")
                    
            else:
                print(f"API error: {result.get('error')}")
        else:
            print(f"HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_advanced_student():
    """Test recommendations for a student with many completed courses"""
    print("\n" + "="*60)
    print("=== CS Recommendations for Advanced Student ===")
    
    test_data = {
        "interests": ["programming", "algorithms", "software engineering"],
        "career_goals": "software_development",
        "difficulty_preference": "any",
        "completed_courses": ["CS114", "CS115", "CS280", "CS288", "CS341", "CS356", "MATH111", "MATH222"],  # Advanced student
        "preferred_topics": ["algorithms", "software engineering"],
        "course_ratings": {},
        "num_recommendations": 10,
        "department_filter": "Computer Science"
    }
    
    try:
        response = requests.post('http://localhost:5000/api/recommend', 
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps(test_data),
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                recommendations = result['recommendations']
                print(f"Found {len(recommendations)} CS recommendations\n")
                
                print("🏆 TOP 10 RECOMMENDED COURSES:")
                for i, course in enumerate(recommendations[:10], 1):
                    level = course.get('level', 'Unknown')
                    match_score = course.get('recommendation_score', 0) * 100
                    
                    if "senior" in level.lower():
                        level_icon = "🔴"
                    elif "junior" in level.lower():
                        level_icon = "🟡"
                    else:
                        level_icon = "🟢"
                    
                    print(f"{i:2}. {level_icon} {course['id']} - {course['title']}")
                    print(f"     Level: {level} | Match: {match_score:.1f}%")
                    print()
                    
            else:
                print(f"API error: {result.get('error')}")
        else:
            print(f"HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_beginner_cs_recommendations()
    test_advanced_student()