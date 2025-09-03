#!/usr/bin/env python3
"""
Debug interest matching specifically
"""

from src.data_manager import DataManager
from src.recommendation_engine import RecommendationEngine

def debug_interest_matching():
    """Debug why interest matching returns 0.000"""
    
    print("=== DEBUGGING INTEREST MATCHING ===\n")
    
    # Initialize components
    data_manager = DataManager()
    engine = RecommendationEngine(data_manager)
    
    # Get CS375 specifically
    courses = data_manager.get_all_courses()
    cs375 = None
    cs301 = None
    
    for course in courses:
        if course['id'] == 'CS375':
            cs375 = course
        elif course['id'] == 'CS301':
            cs301 = course
    
    interests = ['artificial_intelligence', 'machine_learning']
    
    if cs375:
        print("📋 CS375 Course Data:")
        print(f"   ID: {cs375['id']}")
        print(f"   Title: {cs375['title']}")
        print(f"   Description: {cs375.get('description', 'NO DESCRIPTION')[:200]}...")
        print(f"   Topics: {cs375.get('topics', 'NO TOPICS')}")
        print(f"   Career Relevance: {cs375.get('career_relevance', 'NO CAREER')}")
        
        print(f"\n🧠 Testing Interest Matching:")
        print(f"   Student Interests: {interests}")
        
        # Test the function directly
        score = engine.calculate_interest_score(cs375, interests)
        print(f"   Interest Score: {score}")
        
        # Debug the text processing
        course_text = f"{cs375.get('title', '')} {cs375.get('description', '')} {cs375.get('topics', '')}"
        print(f"\n📝 Raw Course Text: {course_text[:200]}...")
        
        processed_course = engine.preprocess_text(course_text)
        print(f"📝 Processed Course Text: {processed_course[:200]}...")
        
        interest_text = ' '.join(interests)
        processed_interest = engine.preprocess_text(interest_text)
        print(f"📝 Processed Interest Text: {processed_interest}")
        
        # Test TF-IDF manually
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        if processed_course and processed_interest:
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            texts = [processed_course, processed_interest]
            tfidf_matrix = vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            print(f"📊 Manual TF-IDF Similarity: {similarity}")
            
            # Show feature names
            feature_names = vectorizer.get_feature_names_out()
            print(f"📊 TF-IDF Features: {list(feature_names)[:20]}...")
        
    else:
        print("❌ CS375 not found in database!")
    
    if cs301:
        print(f"\n📋 CS301 for comparison:")
        print(f"   Title: {cs301['title']}")
        print(f"   Description: {cs301.get('description', 'NO DESCRIPTION')[:100]}...")
        score = engine.calculate_interest_score(cs301, interests)
        print(f"   Interest Score: {score}")
    
    # Test with simpler interests
    print(f"\n🧪 Testing with simpler interests:")
    simple_interests = ['machine', 'learning', 'artificial', 'intelligence']
    if cs375:
        score = engine.calculate_interest_score(cs375, simple_interests)
        print(f"   CS375 with simple interests: {score}")

if __name__ == "__main__":
    debug_interest_matching()