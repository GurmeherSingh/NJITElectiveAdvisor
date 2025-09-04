#!/usr/bin/env python3
"""
Test the new semantic topic matching feature
"""

import requests
import json

def test_semantic_topic_matching():
    """Test semantic topic matching with specific examples"""
    print("🧠 Testing Enhanced Semantic Topic Matching...")
    
    test_scenarios = [
        {
            "name": "Machine Learning Algorithms",
            "specific_topics": "machine learning algorithms, neural networks, deep learning, artificial intelligence",
            "department": "Computer Science",
            "expected_courses": ["CS375", "CS370"]
        },
        {
            "name": "Web Development",
            "specific_topics": "web development, frontend, backend, HTML, CSS, JavaScript, user interfaces",
            "department": "Computer Science", 
            "expected_courses": ["CS280", "CS490"]
        },
        {
            "name": "Data Analysis & Visualization",
            "specific_topics": "data visualization, statistical analysis, data mining, databases, SQL",
            "department": "Data Science",
            "expected_courses": ["DS340", "DS400"]
        },
        {
            "name": "Cybersecurity & Network Protection",
            "specific_topics": "cybersecurity, network security, encryption, attack prevention, digital forensics",
            "department": "Computer Science",
            "expected_courses": ["CS490"]
        },
        {
            "name": "Financial Modeling & Investment",
            "specific_topics": "financial modeling, investment analysis, portfolio management, risk assessment",
            "department": "Finance",
            "expected_courses": ["FIN417", "FIN401"]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        print(f"   Topics: {scenario['specific_topics'][:50]}...")
        
        test_data = {
            "interests": [],
            "specific_topics": scenario['specific_topics'],
            "career_goals": "",
            "difficulty_preference": "any",
            "completed_courses": [],
            "preferred_topics": [],
            "course_ratings": {},
            "num_recommendations": 10,
            "department_filter": scenario['department'],
            "academic_level": "junior"
        }
        
        try:
            response = requests.post('http://localhost:5000/api/recommend',
                                   headers={'Content-Type': 'application/json'},
                                   data=json.dumps(test_data),
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('recommendations'):
                    recommendations = result['recommendations']
                    
                    print(f"   📊 Top 5 Results:")
                    for i, course in enumerate(recommendations[:5], 1):
                        semantic_score = course.get('score_breakdown', {}).get('semantic_topic_match', 0)
                        total_score = course.get('recommendation_score', 0)
                        
                        print(f"      {i}. {course['id']} - {course['title']}")
                        print(f"         Topics: {semantic_score*100:.0f}% | Total: {total_score*100:.0f}%")
                    
                    # Check if expected courses appear in top results
                    top_course_ids = [r['id'] for r in recommendations[:10]]
                    found_expected = []
                    for expected in scenario.get('expected_courses', []):
                        if expected in top_course_ids:
                            rank = top_course_ids.index(expected) + 1
                            found_expected.append(f"{expected} (#{rank})")
                    
                    if found_expected:
                        print(f"   ✅ Expected courses found: {', '.join(found_expected)}")
                    else:
                        print(f"   ⚠️ Expected courses not in top 10: {scenario.get('expected_courses', [])}")
                
                else:
                    print(f"   ❌ No recommendations returned")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_no_specific_topics():
    """Test fallback when no specific topics provided"""
    print(f"\n🤔 Testing with NO specific topics (should fall back gracefully):")
    
    test_data = {
        "interests": ["programming"],
        "specific_topics": "",  # Empty
        "career_goals": "software_development",
        "difficulty_preference": "any",
        "completed_courses": [],
        "preferred_topics": ["programming"],
        "course_ratings": {},
        "num_recommendations": 5,
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
            count = result.get('total_count', 0)
            print(f"   ✅ Successfully returned {count} courses without specific topics")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_semantic_topic_matching()
    test_no_specific_topics()