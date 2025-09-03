#!/usr/bin/env python3
"""
Test the new academic level feature
"""

import requests
import json

def test_different_academic_levels():
    """Test recommendations for different academic levels"""
    
    levels_to_test = [
        ("freshman", "🟢 Freshman"),
        ("sophomore", "🔵 Sophomore"), 
        ("junior", "🟡 Junior"),
        ("senior", "🔴 Senior")
    ]
    
    base_data = {
        "interests": ["programming", "computer science"],
        "career_goals": "software_development",
        "difficulty_preference": "any",
        "completed_courses": [],
        "preferred_topics": ["programming"],
        "course_ratings": {},
        "num_recommendations": 10,
        "department_filter": "Computer Science"
    }
    
    print("=== Testing Academic Level Impact on Recommendations ===\n")
    
    for level_value, level_name in levels_to_test:
        print(f"🎓 Testing for {level_name} student:")
        
        test_data = base_data.copy()
        test_data["academic_level"] = level_value
        
        try:
            response = requests.post('http://localhost:5000/api/recommend', 
                                   headers={'Content-Type': 'application/json'},
                                   data=json.dumps(test_data),
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    recommendations = result['recommendations']
                    
                    # Analyze the top 5 recommendations
                    print(f"  📋 Top 5 Recommendations:")
                    for i, course in enumerate(recommendations[:5], 1):
                        course_level = course.get('level', 'Unknown')
                        match_score = course.get('recommendation_score', 0) * 100
                        level_score = course.get('score_breakdown', {}).get('level_appropriateness', 0) * 100
                        
                        # Add level icon
                        if "senior" in course_level.lower():
                            level_icon = "🔴"
                        elif "junior" in course_level.lower():
                            level_icon = "🟡"
                        elif "sophomore" in course_level.lower():
                            level_icon = "🔵"
                        elif "freshman" in course_level.lower():
                            level_icon = "🟢"
                        else:
                            level_icon = "⚪"
                        
                        print(f"     {i}. {level_icon} {course['id']} - {course['title']}")
                        print(f"        Level: {course_level} | Match: {match_score:.1f}% | Level Score: {level_score:.0f}%")
                    
                    # Count course levels in recommendations
                    level_counts = {}
                    for course in recommendations:
                        course_level = course.get('level', 'Unknown')
                        for level_keyword in ['freshman', 'sophomore', 'junior', 'senior']:
                            if level_keyword in course_level.lower():
                                level_counts[level_keyword] = level_counts.get(level_keyword, 0) + 1
                                break
                        else:
                            level_counts['other'] = level_counts.get('other', 0) + 1
                    
                    print(f"  📊 Course Level Distribution:")
                    for level_key, count in level_counts.items():
                        print(f"     {level_key.title()}: {count} courses")
                    
                else:
                    print(f"  ❌ API error: {result.get('error')}")
            else:
                print(f"  ❌ HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()

def test_no_academic_level():
    """Test with no academic level specified (should fall back to old logic)"""
    print("🤔 Testing with NO academic level specified (fallback behavior):")
    
    test_data = {
        "interests": ["programming", "computer science"],
        "career_goals": "software_development",
        "difficulty_preference": "any",
        "completed_courses": [],
        "preferred_topics": ["programming"],
        "course_ratings": {},
        "num_recommendations": 5,
        "department_filter": "Computer Science"
        # No academic_level specified
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
                print(f"  📋 Top 5 Recommendations (fallback logic):")
                for i, course in enumerate(recommendations[:5], 1):
                    course_level = course.get('level', 'Unknown')
                    match_score = course.get('recommendation_score', 0) * 100
                    print(f"     {i}. {course['id']} - Level: {course_level} | Match: {match_score:.1f}%")
            else:
                print(f"  ❌ API error: {result.get('error')}")
        else:
            print(f"  ❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    test_different_academic_levels()
    test_no_academic_level()