#!/usr/bin/env python3
"""
Debug and analyze recommendation engine issues
"""

import requests
import json

def test_specific_scenario():
    """Test the exact scenario: Sophomore interested in AI/ML"""
    print("=== DEBUGGING: Sophomore + AI/ML Scenario ===\n")
    
    test_data = {
        "interests": ["artificial_intelligence", "machine_learning"],
        "career_goals": "data_science",
        "difficulty_preference": "any",
        "completed_courses": [],
        "preferred_topics": ["artificial_intelligence", "machine_learning"],
        "course_ratings": {},
        "num_recommendations": 15,
        "department_filter": "Computer Science",
        "academic_level": "sophomore"
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
                
                print(f"📊 Found {len(recommendations)} recommendations")
                print("\n🔍 DETAILED SCORING BREAKDOWN for top 10:")
                
                # Look for CS375 specifically
                cs375_found = False
                cs375_rank = None
                
                for i, course in enumerate(recommendations[:15], 1):
                    if course['id'] == 'CS375':
                        cs375_found = True
                        cs375_rank = i
                    
                    scores = course.get('score_breakdown', {})
                    level = course.get('level', 'Unknown')
                    
                    print(f"\n{i}. {course['id']} - {course['title']}")
                    print(f"   Level: {level}")
                    print(f"   TOTAL SCORE: {course.get('recommendation_score', 0):.3f}")
                    print(f"   Interest Match: {scores.get('interest_match', 0):.3f}")
                    print(f"   Career Alignment: {scores.get('career_alignment', 0):.3f}")
                    print(f"   Level Appropriateness: {scores.get('level_appropriateness', 0):.3f}")
                    print(f"   Prerequisites Met: {scores.get('prerequisites_met', 0):.3f}")
                    print(f"   Popularity: {scores.get('popularity', 0):.3f}")
                
                if cs375_found:
                    print(f"\n✅ CS375 found at rank #{cs375_rank}")
                else:
                    print(f"\n❌ CS375 NOT found in top 15!")
                    
                    # Search for CS375 in full results
                    for i, course in enumerate(recommendations):
                        if course['id'] == 'CS375':
                            print(f"   Found CS375 at rank #{i+1}")
                            scores = course.get('score_breakdown', {})
                            print(f"   CS375 TOTAL SCORE: {course.get('recommendation_score', 0):.3f}")
                            print(f"   CS375 Interest: {scores.get('interest_match', 0):.3f}")
                            print(f"   CS375 Career: {scores.get('career_alignment', 0):.3f}")
                            print(f"   CS375 Level: {scores.get('level_appropriateness', 0):.3f}")
                            break
                
            else:
                print(f"❌ API error: {result.get('error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def analyze_weight_distribution():
    """Analyze how the current weights affect scoring"""
    print("\n=== CURRENT WEIGHT ANALYSIS ===")
    print("Current weights (non-exploring mode):")
    print("- Interest Match: 20%")
    print("- Career Alignment: 25%") 
    print("- Level Appropriateness: 20%")
    print("- Prerequisites Met: 20%")
    print("- Popularity: 5%")
    print("- Difficulty: 10%")
    print("\n📝 Issues identified:")
    print("1. Interest/Career weights might be too low vs Level/Prerequisites")
    print("2. Prerequisites heavily penalize advanced courses")
    print("3. Level appropriateness might be working against interest matching")
    print("4. No weight for course number (300-level should rank higher than 100-level)")

if __name__ == "__main__":
    test_specific_scenario()
    analyze_weight_distribution()