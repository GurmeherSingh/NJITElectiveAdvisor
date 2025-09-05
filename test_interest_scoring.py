#!/usr/bin/env python3

from src.recommendation_engine import RecommendationEngine
from src.data_manager import DataManager

def test_architecture_interest_scoring():
    # Initialize properly
    data_manager = DataManager()
    engine = RecommendationEngine(data_manager)

    # Get a real Architecture course
    all_courses = data_manager.get_all_courses()
    arch_course = None
    for course in all_courses:
        if course['id'] == 'ARCH195':  # Architecture Studio I
            arch_course = course
            break
    
    if not arch_course:
        print("Could not find ARCH195 course")
        return
    
    print("=== TESTING ARCHITECTURE INTEREST SCORING ===")
    print(f"Testing course: {arch_course['id']} - {arch_course['title']}")
    print(f"Department: {arch_course['department']}")
    
    # Test interest scoring with Architecture interest
    interest_score = engine.calculate_interest_score(arch_course, ['architecture'])
    print(f"Interest score for Architecture interest: {interest_score}")
    
    # Test if it's detected as architecture course
    is_arch = engine.is_architecture_course(arch_course)
    print(f"Is detected as architecture course: {is_arch}")
    
    # Test with different interests
    print("\n=== TESTING DIFFERENT INTERESTS ===")
    for interest in ['architecture', 'design', 'building', 'construction']:
        score = engine.calculate_interest_score(arch_course, [interest])
        print(f"Interest '{interest}': {score}")
    
    # Test with a non-Architecture course for comparison
    print("\n=== TESTING NON-ARCHITECTURE COURSE ===")
    is_course = None
    for course in all_courses:
        if course['id'] == 'IS431':  # Database Systems
            is_course = course
            break
    
    if is_course:
        print(f"Testing course: {is_course['id']} - {is_course['title']}")
        print(f"Department: {is_course['department']}")
        
        interest_score = engine.calculate_interest_score(is_course, ['architecture'])
        print(f"Interest score for Architecture interest: {interest_score}")
        
        is_arch = engine.is_architecture_course(is_course)
        print(f"Is detected as architecture course: {is_arch}")

if __name__ == "__main__":
    test_architecture_interest_scoring()
