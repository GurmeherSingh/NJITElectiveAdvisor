#!/usr/bin/env python3
"""
Test the new department filter functionality
"""

import requests
import json

def test_department_filters():
    """Test different department filters"""
    
    departments_to_test = [
        ("Computer Science", "CS"),
        ("Information Systems", "IS"), 
        ("Information Technology", "IT"),
        ("Management", "MGMT"),
        ("Accounting", "ACCT"),
        ("Mathematics", "MATH")
    ]
    
    base_data = {
        "interests": ["programming", "technology"],
        "career_goals": "software_development",
        "difficulty_preference": "any",
        "completed_courses": [],
        "preferred_topics": ["programming"],
        "course_ratings": {},
        "num_recommendations": 10
    }
    
    print("=== Testing Department Filters ===\n")
    
    for dept_name, dept_code in departments_to_test:
        print(f"🔍 Testing filter: {dept_name} ({dept_code})")
        
        test_data = base_data.copy()
        test_data["department_filter"] = dept_name
        
        try:
            response = requests.post('http://localhost:5000/api/recommend', 
                                   headers={'Content-Type': 'application/json'},
                                   data=json.dumps(test_data),
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    recommendations = result['recommendations']
                    print(f"  ✅ Found {len(recommendations)} courses")
                    
                    # Verify all courses are from the right department
                    correct_dept = all(course.get('department') == dept_name for course in recommendations)
                    
                    if correct_dept:
                        print(f"  ✅ All courses are from {dept_name}")
                    else:
                        print(f"  ❌ Some courses are from other departments!")
                        for course in recommendations[:3]:
                            print(f"    - {course['id']}: {course.get('department', 'Unknown')}")
                    
                    # Show a few examples
                    print(f"  📋 Sample courses:")
                    for course in recommendations[:3]:
                        prereqs = course.get('prerequisites', 'None')
                        if len(prereqs) > 50:
                            prereqs = prereqs[:47] + "..."
                        print(f"    - {course['id']}: {course['title']}")
                        print(f"      Prerequisites: {prereqs}")
                    
                else:
                    print(f"  ❌ API error: {result.get('error')}")
            else:
                print(f"  ❌ HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()

def test_no_filter():
    """Test with no department filter (should return mixed departments)"""
    print("🌐 Testing with NO department filter (should return mixed departments)")
    
    test_data = {
        "interests": ["programming", "technology"],
        "career_goals": "software_development", 
        "difficulty_preference": "any",
        "completed_courses": [],
        "preferred_topics": ["programming"],
        "course_ratings": {},
        "num_recommendations": 15,
        "department_filter": ""  # No filter
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
                print(f"✅ Found {len(recommendations)} courses from mixed departments")
                
                # Count departments
                dept_counts = {}
                for course in recommendations:
                    dept = course.get('department', 'Unknown')
                    dept_counts[dept] = dept_counts.get(dept, 0) + 1
                
                print("📊 Department breakdown:")
                for dept, count in sorted(dept_counts.items()):
                    print(f"  {dept}: {count} courses")
                    
            else:
                print(f"❌ API error: {result.get('error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_department_filters()
    test_no_filter()