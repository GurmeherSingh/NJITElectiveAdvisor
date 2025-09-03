import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class RecommendationEngine:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scaler = StandardScaler()
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english')) if nltk.data.find('corpora/stopwords') else set()
        
        # Comprehensive career goal to course topic mapping
        self.career_mappings = {
            # Technology & Computing
            'software_development': ['software engineering', 'programming', 'web development', 'mobile development', 'system design'],
            'data_science': ['machine learning', 'data mining', 'statistics', 'analytics', 'big data', 'visualization'],
            'cybersecurity': ['security', 'cryptography', 'network security', 'ethical hacking', 'information security'],
            'ai_ml': ['artificial intelligence', 'machine learning', 'neural networks', 'deep learning', 'robotics'],
            'web_development': ['web development', 'frontend', 'backend', 'javascript', 'databases', 'user interface'],
            'mobile_development': ['mobile development', 'android', 'ios', 'app development', 'user experience'],
            'game_development': ['game development', 'computer graphics', 'animation', 'game design', 'interactive'],
            'network_engineering': ['networking', 'protocols', 'distributed systems', 'cloud computing', 'infrastructure'],
            'database_administration': ['databases', 'sql', 'data management', 'database design', 'information systems'],
            
            # Engineering
            'mechanical_engineering': ['mechanical', 'robotics', 'automation', 'manufacturing', 'design', 'materials'],
            'civil_engineering': ['civil', 'construction', 'infrastructure', 'environmental', 'sustainability', 'transportation'],
            'biomedical_engineering': ['biomedical', 'medical devices', 'healthcare', 'biomaterials', 'biotechnology'],
            'chemical_engineering': ['chemical', 'process engineering', 'biotechnology', 'materials', 'environmental'],
            'electrical_engineering': ['electrical', 'electronics', 'signal processing', 'communications', 'power systems'],
            'robotics_engineering': ['robotics', 'automation', 'mechatronics', 'control systems', 'artificial intelligence'],
            'environmental_engineering': ['environmental', 'sustainability', 'green', 'renewable', 'pollution control'],
            
            # Business & Management
            'entrepreneur': ['entrepreneurship', 'startups', 'innovation', 'business development', 'venture capital'],
            'product_manager': ['product management', 'project management', 'innovation', 'user experience', 'strategy'],
            'project_manager': ['project management', 'leadership', 'operations', 'planning', 'coordination'],
            'business_analyst': ['business analytics', 'data analysis', 'decision making', 'strategy', 'optimization'],
            'consultant': ['consulting', 'strategy', 'problem solving', 'analysis', 'communication'],
            'operations_manager': ['operations', 'management', 'optimization', 'logistics', 'efficiency'],
            
            # Science & Research
            'research_scientist': ['research', 'analysis', 'methodology', 'experimentation', 'innovation'],
            'biotechnology': ['biotechnology', 'biology', 'genetics', 'bioprocessing', 'pharmaceuticals'],
            'data_analyst': ['data analysis', 'statistics', 'research', 'visualization', 'modeling'],
            'laboratory_scientist': ['laboratory', 'research', 'analysis', 'testing', 'experimentation'],
            'environmental_scientist': ['environmental', 'sustainability', 'ecology', 'research', 'conservation'],
            
            # Design & Creative
            'ux_designer': ['user experience', 'design', 'interface', 'usability', 'human factors'],
            'architect': ['architecture', 'design', 'building', 'sustainability', 'planning'],
            'design_engineer': ['design', 'engineering', 'product development', 'innovation', 'creativity'],
            'creative_director': ['design', 'creativity', 'visual', 'communication', 'leadership'],
            
            # Other/Exploring
            'academia': ['research', 'teaching', 'analysis', 'theory', 'methodology'],
            'government': ['policy', 'public service', 'analysis', 'administration', 'planning'],
            'non_profit': ['social impact', 'sustainability', 'community', 'advocacy', 'research'],
            'exploring': ['interdisciplinary', 'diverse', 'broad', 'exploratory', 'foundation'],
            'interdisciplinary': ['interdisciplinary', 'cross-functional', 'diverse', 'integrated', 'holistic'],
            
            # Legacy mappings for compatibility
            'research': ['research', 'algorithms', 'theory', 'computational complexity', 'research methods']
        }
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        if not text:
            return ""
        
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        
        # Tokenize and remove stopwords
        words = word_tokenize(text)
        words = [self.stemmer.stem(word) for word in words if word not in self.stop_words]
        
        return ' '.join(words)
    
    def calculate_interest_score(self, course: Dict, interests: List[str]) -> float:
        """Calculate how well a course matches student interests"""
        if not interests:
            return 0.5  # Neutral score
        
        course_text = f"{course.get('title', '')} {course.get('description', '')} {course.get('topics', '')}"
        course_text = self.preprocess_text(course_text)
        
        interest_text = ' '.join(interests)
        interest_text = self.preprocess_text(interest_text)
        
        if not course_text or not interest_text:
            return 0.5
        
        # Use TF-IDF similarity
        try:
            texts = [course_text, interest_text]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            return 0.5
    
    def calculate_career_score(self, course: Dict, career_goals: str, is_exploring: bool = False) -> float:
        """Calculate how well a course aligns with career goals"""
        if not career_goals and not is_exploring:
            return 0.5
        
        # If exploring, give bonus to diverse departments and interdisciplinary courses
        if is_exploring or career_goals in ['exploring', 'interdisciplinary']:
            course_dept = course.get('department', '').lower()
            course_topics = course.get('topics', '').lower()
            course_relevance = course.get('career_relevance', '').lower()
            
            # Bonus for interdisciplinary keywords
            interdisciplinary_bonus = 0.0
            interdisciplinary_keywords = ['interdisciplinary', 'cross-functional', 'diverse', 'innovation', 'creative']
            for keyword in interdisciplinary_keywords:
                if keyword in course_topics or keyword in course_relevance:
                    interdisciplinary_bonus += 0.1
            
            # Bonus for non-CS departments to encourage exploration
            non_cs_bonus = 0.2 if 'computer science' not in course_dept else 0.0
            
            return min(0.7 + interdisciplinary_bonus + non_cs_bonus, 1.0)
        
        career_goals_lower = career_goals.lower()
        course_relevance = course.get('career_relevance', '').lower()
        course_topics = course.get('topics', '').lower()
        
        # Direct keyword matching
        score = 0.0
        career_keywords = career_goals_lower.split()
        
        for keyword in career_keywords:
            if keyword in course_relevance:
                score += 0.3
            if keyword in course_topics:
                score += 0.2
        
        # Check career mappings
        for career_type, keywords in self.career_mappings.items():
            if career_type == career_goals or any(keyword in career_goals_lower for keyword in [career_type.replace('_', ' ')]):
                for topic_keyword in keywords:
                    if topic_keyword in course_relevance or topic_keyword in course_topics:
                        score += 0.25
        
        return min(score, 1.0)  # Cap at 1.0
    
    def calculate_difficulty_score(self, course: Dict, difficulty_preference: str) -> float:
        """Calculate difficulty alignment score"""
        course_difficulty = course.get('difficulty_rating', 3.0)
        
        difficulty_map = {
            'easy': 2.0,
            'medium': 3.5,
            'hard': 4.5,
            'any': 3.5
        }
        
        preferred_difficulty = difficulty_map.get(difficulty_preference.lower(), 3.5)
        
        # Calculate score based on how close the difficulties are
        diff = abs(course_difficulty - preferred_difficulty)
        score = max(0, 1 - (diff / 2.0))  # Normalize to 0-1 range
        
        return score
    
    def calculate_prerequisite_score(self, course: Dict, completed_courses: List[str]) -> float:
        """Check if student has completed prerequisites"""
        prerequisites = course.get('prerequisites', '')
        if not prerequisites or prerequisites.lower() in ['none', 'n/a']:
            return 1.0
        
        # Extract course codes from prerequisites string
        prereq_codes = re.findall(r'[A-Z]{2,4}\d{3}', prerequisites.upper())
        
        if not prereq_codes:
            return 1.0  # Assume satisfied if we can't parse prerequisites
        
        completed_upper = [code.upper() for code in completed_courses]
        satisfied_count = sum(1 for prereq in prereq_codes if prereq in completed_upper)
        
        return satisfied_count / len(prereq_codes) if prereq_codes else 1.0
    
    def calculate_popularity_score(self, course: Dict) -> float:
        """Calculate course popularity/quality score based on student ratings"""
        avg_rating = course.get('avg_rating', 0)
        total_ratings = course.get('total_ratings', 0)
        
        # Normalize rating (1-5 scale)
        if avg_rating > 0:
            rating_score = (avg_rating - 1) / 4
        else:
            # Fall back to estimated rating if no student ratings yet
            estimated_rating = course.get('rating', 3.0)
            rating_score = (estimated_rating - 1) / 4
        
        # Confidence score based on number of ratings
        confidence_score = min(total_ratings / 10, 1.0)  # Full confidence at 10+ ratings
        
        # Weighted combination: prioritize courses with student ratings
        if total_ratings > 0:
            return 0.8 * rating_score + 0.2 * confidence_score
        else:
            return 0.5 * rating_score  # Lower weight for estimated ratings
    
    def get_recommendations(self, interests: List[str], career_goals: str, 
                          preferred_topics: List[str], difficulty_preference: str = 'medium',
                          completed_courses: List[str] = None, num_recommendations: int = 10) -> List[Dict]:
        """
        Generate course recommendations based on student preferences
        """
        if completed_courses is None:
            completed_courses = []
        
        # Check if user wants to explore new fields
        is_exploring = 'explore new fields discover interdisciplinary' in ' '.join(interests + preferred_topics)
        
        # Get all courses
        all_courses = self.data_manager.get_all_courses()
        
        if not all_courses:
            return []
        
        # Calculate scores for each course
        recommendations = []
        
        for course in all_courses:
            # Skip if already completed
            if course['id'] in completed_courses:
                continue
            
            # Calculate individual scores
            interest_score = self.calculate_interest_score(course, interests + preferred_topics)
            career_score = self.calculate_career_score(course, career_goals, is_exploring)
            difficulty_score = self.calculate_difficulty_score(course, difficulty_preference)
            prerequisite_score = self.calculate_prerequisite_score(course, completed_courses)
            popularity_score = self.calculate_popularity_score(course)
            
            # Adjust weights for exploration mode
            if is_exploring:
                # Give more weight to career/exploration and less to specific interests
                final_score = (
                    0.15 * interest_score +      # Reduced from 0.25
                    0.40 * career_score +        # Increased from 0.30
                    0.15 * difficulty_score +
                    0.20 * prerequisite_score +
                    0.10 * popularity_score
                )
            else:
                # Normal weighting
                final_score = (
                    0.25 * interest_score +
                    0.30 * career_score +
                    0.15 * difficulty_score +
                    0.20 * prerequisite_score +
                    0.10 * popularity_score
                )

            
            # Add recommendation with detailed scoring
            recommendation = {
                **course,
                'recommendation_score': round(final_score, 3),
                'score_breakdown': {
                    'interest_match': round(interest_score, 3),
                    'career_alignment': round(career_score, 3),
                    'difficulty_fit': round(difficulty_score, 3),
                    'prerequisites_met': round(prerequisite_score, 3),
                    'popularity': round(popularity_score, 3)
                },
                'recommendation_reason': self.generate_recommendation_reason(
                    course, interest_score, career_score, difficulty_score, prerequisite_score
                )
            }
            
            recommendations.append(recommendation)
        
        # Sort by recommendation score and return top N
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return recommendations[:num_recommendations]
    
    def generate_recommendation_reason(self, course: Dict, interest_score: float, 
                                     career_score: float, difficulty_score: float, 
                                     prerequisite_score: float) -> str:
        """Generate human-readable recommendation explanation"""
        reasons = []
        
        if interest_score > 0.7:
            reasons.append("strongly matches your interests")
        elif interest_score > 0.5:
            reasons.append("aligns with your interests")
        
        if career_score > 0.7:
            reasons.append("highly relevant to your career goals")
        elif career_score > 0.5:
            reasons.append("supports your career objectives")
        
        if difficulty_score > 0.8:
            reasons.append("perfect difficulty level for you")
        elif difficulty_score > 0.6:
            reasons.append("appropriate difficulty level")
        
        if prerequisite_score >= 1.0:
            reasons.append("you meet all prerequisites")
        elif prerequisite_score > 0.5:
            reasons.append("you meet most prerequisites")
        
        if course.get('rating', 0) > 4.0:
            reasons.append("highly rated by students")
        
        if not reasons:
            reasons.append("good foundational course for your profile")
        
        return f"Recommended because it {', '.join(reasons[:3])}."
    
    def get_similar_courses(self, course_id: str, num_similar: int = 5) -> List[Dict]:
        """Find courses similar to a given course"""
        target_course = self.data_manager.get_course_by_id(course_id)
        if not target_course:
            return []
        
        all_courses = self.data_manager.get_all_courses()
        similarities = []
        
        target_text = f"{target_course.get('description', '')} {target_course.get('topics', '')}"
        target_text = self.preprocess_text(target_text)
        
        for course in all_courses:
            if course['id'] == course_id:
                continue
            
            course_text = f"{course.get('description', '')} {course.get('topics', '')}"
            course_text = self.preprocess_text(course_text)
            
            try:
                texts = [target_text, course_text]
                tfidf_matrix = self.vectorizer.fit_transform(texts)
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                similarities.append((course, similarity))
            except:
                similarities.append((course, 0.0))
        
        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return [{'course': course, 'similarity_score': score} 
                for course, score in similarities[:num_similar]]