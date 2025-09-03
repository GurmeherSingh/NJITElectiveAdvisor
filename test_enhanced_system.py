#!/usr/bin/env python3
"""
Test Enhanced NJIT Elective Advisor System
"""

from src.recommendation_engine import RecommendationEngine
from src.data_manager import DataManager

def test_enhanced_recommendations():
    print("🎓 Testing Enhanced NJIT Elective Advisor")
    print("=" * 60)
    
    # Initialize
    dm = DataManager()
    re = RecommendationEngine(dm)
    
    # Test 1: Business/Entrepreneurship Interest
    print("1. 🚀 Testing Business/Entrepreneurship Interest:")
    interests = ['entrepreneurship startups innovation business']
    career_goal = 'entrepreneur'
    recs = re.get_recommendations(interests, career_goal, [], 'medium', [])
    
    print(f"   Found {len(recs)} recommendations:")
    for i, rec in enumerate(recs[:5], 1):
        print(f"   {i}. {rec['id']} - {rec['title']}")
        print(f"      Department: {rec['department']}")
        print(f"      Match: {rec['recommendation_score']:.1%}")
        print()
    
    # Test 2: Exploration Mode
    print("2. 🧭 Testing Exploration Mode:")
    interests = ['explore new fields discover interdisciplinary']
    career_goal = 'exploring'
    recs = re.get_recommendations(interests, career_goal, [], 'medium', [])
    
    print(f"   Found {len(recs)} recommendations:")
    departments = set()
    for i, rec in enumerate(recs[:5], 1):
        departments.add(rec['department'])
        print(f"   {i}. {rec['id']} - {rec['title']}")
        print(f"      Department: {rec['department']}")
        print(f"      Match: {rec['recommendation_score']:.1%}")
        print()
    
    print(f"   Departments represented: {len(departments)}")
    print(f"   Departments: {', '.join(sorted(departments))}")
    
    # Test 3: Biology Interest
    print("3. 🧬 Testing Biology/Biotech Interest:")
    interests = ['biology biotechnology life sciences']
    career_goal = 'biotechnology'
    recs = re.get_recommendations(interests, career_goal, [], 'medium', [])
    
    print(f"   Found {len(recs)} recommendations:")
    for i, rec in enumerate(recs[:3], 1):
        print(f"   {i}. {rec['id']} - {rec['title']}")
        print(f"      Department: {rec['department']}")
        print(f"      Match: {rec['recommendation_score']:.1%}")
        print()
    
    # Test 4: Architecture/Design Interest
    print("4. 🏗️ Testing Architecture/Design Interest:")
    interests = ['architecture sustainable design building']
    career_goal = 'architect'
    recs = re.get_recommendations(interests, career_goal, [], 'medium', [])
    
    print(f"   Found {len(recs)} recommendations:")
    for i, rec in enumerate(recs[:3], 1):
        print(f"   {i}. {rec['id']} - {rec['title']}")
        print(f"      Department: {rec['department']}")
        print(f"      Match: {rec['recommendation_score']:.1%}")
        print()
    
    # Summary
    all_courses = dm.get_all_courses()
    departments = set(course['department'] for course in all_courses)
    
    print("📊 System Summary:")
    print(f"   Total Courses: {len(all_courses)}")
    print(f"   Total Departments: {len(departments)}")
    print(f"   Departments: {', '.join(sorted(departments))}")
    
    print("\n✅ Enhanced system test complete!")
    print("🎯 Students can now:")
    print("   • Explore electives across ALL NJIT departments")
    print("   • Discover new fields outside their major") 
    print("   • Get recommendations for non-tech careers")
    print("   • Use the exploration mode to find interdisciplinary courses")

if __name__ == "__main__":
    test_enhanced_recommendations()