#!/usr/bin/env python3
"""
Debug CS375 ML course recommendations
"""

import requests
import json

def test_cs375_for_sophomore():
    """Test CS375 specifically for sophomore AI/ML interest"""
    
    print("🔍 Debugging CS375 for Sophomore AI/ML student")
    print("=" * 50)
    
    test_data = {
        "interests": ["artificial_intelligence", "machine_learning", "programming"],
        "career_goals": "ai_ml_engineer", 
        "difficulty_preference": "any",
        "completed_courses": ["CS115", "CS116"],  # Typical sophomore
        "preferred_topics": ["artificial_intelligence", "machine_learning"],
        "course_ratings": {},
        "num_recommendations": 20,
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
                
                print(f"📊 Total recommendations: {len(recommendations)}")
                print()
                
                # Find CS375 specifically
                cs375_found = None
                cs375_position = None
                
                for i, course in enumerate(recommendations):
                    if course['id'] == 'CS375':
                        cs375_found = course
                        cs375_position = i + 1
                        break
                
                if cs375_found:
                    print(f"✅ CS375 FOUND at position #{cs375_position}")
                    print(f"   Title: {cs375_found['title']}")
                    print(f"   Level: {cs375_found.get('level', 'Unknown')}")
                    print(f"   Overall Score: {cs375_found['recommendation_score']:.3f}")
                    print(f"   Score Breakdown:")
                    breakdown = cs375_found.get('score_breakdown', {})
                    for metric, score in breakdown.items():
                        print(f"     {metric}: {score:.3f}")
                    print()
                else:
                    print("❌ CS375 NOT FOUND in recommendations!")
                    print("   Let me check what courses we do have...")
                    print()
                
                # Show top 10 with detailed scoring
                print("🏆 Top 10 Recommendations with Detailed Scoring:")
                for i, course in enumerate(recommendations[:10], 1):
                    breakdown = course.get('score_breakdown', {})
                    level_icon = "🟢" if "freshman" in course.get('level', '').lower() else \
                                "🔵" if "sophomore" in course.get('level', '').lower() else \
                                "🟡" if "junior" in course.get('level', '').lower() else \
                                "🔴" if "senior" in course.get('level', '').lower() else "⚪"
                    
                    print(f"{i:2d}. {level_icon} {course['id']} - {course['title']}")
                    print(f"     Level: {course.get('level', 'Unknown')} | Overall: {course['recommendation_score']:.3f}")
                    print(f"     Interest: {breakdown.get('interest_match', 0):.2f} | "
                          f"Career: {breakdown.get('career_alignment', 0):.2f} | "
                          f"Level: {breakdown.get('level_appropriateness', 0):.2f}")
                    print()
                
                # Check for other ML-related courses
                ml_courses = []
                for course in recommendations:
                    course_text = f"{course['id']} {course['title']} {course.get('description', '')}".lower()
                    if any(term in course_text for term in ['machine learning', 'artificial intelligence', 'neural', 'ai', 'ml']):
                        ml_courses.append(course)
                
                if ml_courses:
                    print(f"🤖 Found {len(ml_courses)} ML/AI related courses:")
                    for course in ml_courses[:5]:
                        pos = next((i+1 for i, c in enumerate(recommendations) if c['id'] == course['id']), 'Not found')
                        print(f"   #{pos}: {course['id']} - {course['title']}")
                
            else:
                print(f"❌ API error: {result.get('error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def check_cs375_in_database():
    """Check if CS375 exists in our database"""
    print("\n🗄️ Checking CS375 in database...")
    
    try:
        import sqlite3
        conn = sqlite3.connect('courses.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM courses WHERE id = 'CS375'")
        result = cursor.fetchone()
        
        if result:
            print("✅ CS375 found in database!")
            # Get column names
            cursor.execute("PRAGMA table_info(courses)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Print course details
            course_dict = dict(zip(columns, result))
            for key, value in course_dict.items():
                print(f"   {key}: {value}")
        else:
            print("❌ CS375 NOT found in database!")
            
            # Check what CS courses we do have
            cursor.execute("SELECT id, title FROM courses WHERE id LIKE 'CS%' ORDER BY id")
            cs_courses = cursor.fetchall()
            print(f"\n📚 Found {len(cs_courses)} CS courses in database:")
            for course_id, title in cs_courses[:10]:
                print(f"   {course_id}: {title}")
            if len(cs_courses) > 10:
                print(f"   ... and {len(cs_courses) - 10} more")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_cs375_in_database()
    test_cs375_for_sophomore()