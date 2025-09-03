#!/usr/bin/env python3
"""
Test to see why senior courses are ranking so high
"""

import requests
import json
from src.recommendation_engine import RecommendationEngine
from src.data_manager import DataManager

def test_scoring_breakdown():
    """Test scoring for different types of courses"""
    
    data_manager = DataManager()
    engine = RecommendationEngine(data_manager)
    
    # Test different course types
    test_courses = [
        # Senior course with standing prerequisite
        {"id": "TEST_SENIOR", "prerequisites": "Senior standing", "level": "Senior", "difficulty_rating": "High", "department": "Computer Science"},
        # Intro course with no prerequisites  
        {"id": "TEST_INTRO", "prerequisites": "", "level": "Freshman", "difficulty_rating": "Low", "department": "Computer Science"},
        # Advanced course with actual prerequisites
        {"id": "TEST_ADVANCED", "prerequisites": "CS280, CS288", "level": "Junior", "difficulty_rating": "High", "department": "Computer Science"},
    ]
    
    # Test with beginner student (no completed courses)
    completed_courses = []
    interests = ["programming", "computer science"]
    career_goals = "software_development"
    
    print("=== Scoring Breakdown for Different Course Types ===\n")
    
    for course in test_courses:
        print(f"🔍 Course: {course['id']} ({course['level']} level)")
        print(f"   Prerequisites: '{course['prerequisites']}'")
        
        # Calculate individual scores
        interest_score = engine.calculate_interest_score(course, interests)
        career_score = engine.calculate_career_score(course, career_goals, False)
        difficulty_score = engine.calculate_difficulty_score(course, 'any')
        prerequisite_score = engine.calculate_prerequisite_score(course, completed_courses)
        popularity_score = engine.calculate_popularity_score(course)
        
        # Calculate final score (normal weighting)
        final_score = (
            0.25 * interest_score +
            0.30 * career_score +
            0.15 * difficulty_score +
            0.20 * prerequisite_score +
            0.10 * popularity_score
        )
        
        print(f"   📊 Score Breakdown:")
        print(f"      Interest (25%): {interest_score:.3f}")
        print(f"      Career (30%): {career_score:.3f}")
        print(f"      Difficulty (15%): {difficulty_score:.3f}")
        print(f"      Prerequisites (20%): {prerequisite_score:.3f}")
        print(f"      Popularity (10%): {popularity_score:.3f}")
        print(f"      🎯 FINAL SCORE: {final_score:.3f}")
        print()

def test_actual_recommendations():
    """Test actual API recommendations to see course levels"""
    print("=== Testing Actual API Recommendations ===")
    
    test_data = {
        "interests": ["programming", "computer science"],
        "career_goals": "software_development",
        "difficulty_preference": "any",
        "completed_courses": [],  # Beginner student
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
                
                for i, course in enumerate(recommendations[:10], 1):
                    level = course.get('level', 'Unknown')
                    prereqs = course.get('prerequisites', 'None')
                    if len(prereqs) > 40:
                        prereqs = prereqs[:37] + "..."
                    
                    match_score = course.get('recommendation_score', 0) * 100
                    
                    # Identify course type
                    course_type = "🟢 INTRO"
                    if "senior" in level.lower() or "capstone" in course['title'].lower():
                        course_type = "🔴 SENIOR"
                    elif prereqs and any(code in prereqs.upper() for code in ['CS2', 'CS3', 'CS4', 'MATH2', 'MATH3']):
                        course_type = "🟡 ADVANCED"
                    
                    print(f"{i:2}. {course_type} {course['id']} - {course['title']}")
                    print(f"     Level: {level} | Match: {match_score:.0f}% | Prerequisites: {prereqs}")
                    print()
                    
            else:
                print(f"API error: {result.get('error')}")
        else:
            print(f"HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_scoring_breakdown()
    test_actual_recommendations()