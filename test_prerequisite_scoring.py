#!/usr/bin/env python3
"""
Test prerequisite scoring logic
"""

from src.recommendation_engine import RecommendationEngine
from src.data_manager import DataManager
import re

def test_prerequisite_parsing():
    """Test how different prerequisite formats are parsed"""
    
    test_cases = [
        "CS280, CS288",
        "ACCT115 or ACCT117", 
        "Junior standing",
        "Senior standing",
        "None",
        "",
        "Business and fintech majors restriction",
        "Programming and statistics prerequisites",
        "CS114/CS116/IT114",
        "MATH111 or MATH135"
    ]
    
    print("=== Testing Prerequisite Parsing ===")
    
    for prereq in test_cases:
        # Extract course codes using the same regex as the engine
        prereq_codes = re.findall(r'[A-Z]{2,4}\d{3}', prereq.upper())
        print(f"Prerequisites: '{prereq}'")
        print(f"Extracted codes: {prereq_codes}")
        print(f"Would return 1.0? {len(prereq_codes) == 0}")
        print("---")

def test_prerequisite_scoring_logic():
    """Test the actual scoring logic"""
    print("\n=== Testing Prerequisite Scoring Logic ===")
    
    data_manager = DataManager()
    engine = RecommendationEngine(data_manager)
    
    # Test different scenarios
    test_courses = [
        {"id": "TEST1", "prerequisites": "CS280, CS288"},
        {"id": "TEST2", "prerequisites": "Junior standing"}, 
        {"id": "TEST3", "prerequisites": "None"},
        {"id": "TEST4", "prerequisites": ""},
        {"id": "TEST5", "prerequisites": "ACCT115 or ACCT117"},
    ]
    
    completed_courses_scenarios = [
        [],  # No completed courses
        ["CS280"],  # Some completed
        ["CS280", "CS288", "ACCT115"],  # More completed
    ]
    
    for completed in completed_courses_scenarios:
        print(f"\nCompleted courses: {completed}")
        for course in test_courses:
            score = engine.calculate_prerequisite_score(course, completed)
            print(f"  {course['id']} ('{course['prerequisites']}'): {score:.2f}")

if __name__ == "__main__":
    test_prerequisite_parsing()
    test_prerequisite_scoring_logic()