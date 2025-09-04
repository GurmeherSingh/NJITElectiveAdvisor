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
except Exception as e:
    # Fallback for production environments where downloads might fail
    print(f"NLTK download warning: {e}")
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
        
        # Enhanced keyword expansion for better cross-department matching
        expanded_interests = []
        
        # Comprehensive keyword mappings for better cross-department matching
        ENHANCED_KEYWORDS = {
            'cybersecurity': [
                'security', 'cyber', 'cybersecurity', 'encryption', 'firewall', 
                'network security', 'information security', 'protection', 'vulnerability',
                'authentication', 'authorization', 'cryptography', 'secure', 'privacy',
                'risk management', 'threat', 'defense', 'forensics', 'penetration',
                'malware', 'intrusion', 'incident response', 'compliance'
            ],
            'ux_design': [
                'user experience', 'user interface', 'ui', 'ux', 'usability', 
                'human computer interaction', 'interface design', 'user centered',
                'interaction design', 'user research', 'design thinking', 'hci',
                'user needs', 'user testing', 'prototyping', 'wireframe',
                'accessibility', 'ergonomics', 'human factors', 'persona'
            ],
            'mechanical_engineering': [
                'mechanical', 'engineering design', 'manufacturing', 'systems design',
                'product design', 'cad', 'modeling', 'simulation', 'automation',
                'robotics', 'control systems', 'mechanics', 'materials', 'thermal',
                'fluid dynamics', 'design optimization', 'prototype', 'machining',
                'assembly', 'tolerance', 'quality', 'reliability', 'testing',
                'production', 'process design', 'tooling', 'fixtures'
            ],
            'environmental_science': [
                'environmental', 'sustainability', 'ecology', 'climate', 'green',
                'renewable', 'conservation', 'environmental data', 'gis',
                'remote sensing', 'environmental monitoring', 'pollution',
                'ecosystem', 'biodiversity', 'carbon', 'energy efficiency',
                'water quality', 'air quality', 'soil', 'waste management',
                'environmental impact', 'assessment', 'geographic', 'spatial'
            ],
            'architecture': [
                'architecture', 'architectural', 'building design', 'structural',
                'construction', 'spatial design', 'urban planning', 'design',
                'modeling', 'visualization', '3d modeling', 'cad', 'drafting',
                'building systems', 'sustainable design', 'space planning'
            ],
            'web_development': [
                'web', 'website', 'html', 'css', 'javascript', 'frontend', 'backend',
                'react', 'node', 'express', 'http', 'api', 'rest', 'json',
                'responsive', 'bootstrap', 'jquery', 'php', 'mysql'
            ],
            'data_science': [
                'data science', 'data analysis', 'statistics', 'analytics',
                'visualization', 'machine learning', 'big data', 'pandas',
                'python', 'r', 'sql', 'database', 'mining', 'warehouse'
            ],
            'mobile_development': [
                'mobile', 'android', 'ios', 'app development', 'smartphone',
                'tablet', 'swift', 'kotlin', 'react native', 'flutter'
            ],
            'game_development': [
                'game', 'gaming', 'unity', 'graphics', '3d', 'animation',
                'interactive', 'simulation', 'physics', 'rendering'
            ],
            # New interests - using exact form values as keys
            'cloud computing devops aws azure infrastructure': [
                'cloud', 'aws', 'azure', 'devops', 'infrastructure', 'kubernetes',
                'docker', 'containerization', 'microservices', 'serverless',
                'deployment', 'ci/cd', 'automation', 'scalability', 'virtualization'
            ],
            'mobile development ios android apps': [
                'mobile', 'android', 'ios', 'app development', 'smartphone',
                'tablet', 'swift', 'kotlin', 'react native', 'flutter'
            ],
            'game development unity programming graphics': [
                'game', 'gaming', 'unity', 'graphics', '3d', 'animation',
                'interactive', 'simulation', 'physics', 'rendering'
            ],
            'electrical engineering electronics circuits power': [
                'electrical', 'electronics', 'circuits', 'power', 'signal processing',
                'communications', 'control systems', 'embedded systems', 'vlsi',
                'analog', 'digital', 'microprocessors', 'sensors', 'instrumentation'
            ],
            'industrial engineering operations supply chain systems': [
                'industrial', 'operations', 'supply chain', 'systems', 'optimization',
                'lean', 'six sigma', 'quality', 'productivity', 'logistics',
                'ergonomics', 'human factors', 'process improvement', 'efficiency'
            ],
            'environmental engineering sustainability green technology': [
                'environmental engineering', 'sustainability', 'green technology',
                'water treatment', 'air pollution', 'waste management', 'remediation',
                'renewable energy', 'environmental impact', 'ecology'
            ],
            'finance accounting economics financial analysis': [
                'finance', 'accounting', 'economics', 'financial analysis', 'investment',
                'banking', 'financial modeling', 'risk management', 'portfolio',
                'budgeting', 'cost accounting', 'auditing', 'taxation'
            ],
            'physics engineering physics applied physics': [
                'physics', 'engineering physics', 'applied physics', 'quantum',
                'mechanics', 'thermodynamics', 'electromagnetism', 'optics',
                'nuclear', 'computational physics', 'materials physics'
            ],
            'communication media journalism public relations': [
                'communication', 'media', 'journalism', 'public relations', 'writing',
                'reporting', 'broadcasting', 'digital media', 'social media',
                'public speaking', 'rhetoric', 'mass communication', 'storytelling'
            ],
            'science technology society ethics innovation policy': [
                'science technology society', 'sts', 'ethics', 'policy', 'innovation',
                'social impact', 'technology ethics', 'digital divide', 'sustainability',
                'environmental policy', 'science policy', 'technology assessment',
                'social responsibility', 'public understanding', 'science communication'
            ],
            'psychology human behavior cognitive science': [
                'psychology', 'human behavior', 'cognitive science', 'mental health',
                'research methods', 'social psychology', 'behavioral', 'perception',
                'learning', 'memory', 'decision making', 'human factors'
            ],
            'theatre performing arts drama production': [
                'theatre', 'performing arts', 'drama', 'production', 'acting',
                'directing', 'stage design', 'lighting', 'sound', 'costume',
                'performance', 'creative writing', 'dramatic arts'
            ],
            'history humanities culture literature': [
                'history', 'humanities', 'culture', 'literature', 'philosophy',
                'anthropology', 'sociology', 'cultural studies', 'critical thinking',
                'research', 'writing', 'analysis', 'interpretation'
            ],
            'health wellness physical education sports': [
                'health', 'wellness', 'physical education', 'sports', 'fitness',
                'nutrition', 'exercise science', 'kinesiology', 'public health',
                'healthcare', 'medicine', 'therapy', 'rehabilitation'
            ]
        }
        
        for interest in interests:
            # Add enhanced keywords for specific interests
            if interest.lower() in ENHANCED_KEYWORDS:
                expanded_interests.extend(ENHANCED_KEYWORDS[interest.lower()])
            
            # Split compound words and add both compound and separate versions
            if '_' in interest:
                parts = interest.split('_')
                expanded_interests.extend(parts)  # Add individual words
                expanded_interests.append(interest.replace('_', ' '))  # Add as phrase
            else:
                expanded_interests.append(interest)
        
        interest_text = ' '.join(expanded_interests)
        interest_text = self.preprocess_text(interest_text)
        
        if not course_text or not interest_text:
            return 0.5
        
        # Enhanced matching: TF-IDF + keyword overlap
        score = 0.0
        
        # 1. TF-IDF similarity (60% weight)
        try:
            texts = [course_text, interest_text]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            tfidf_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            score += 0.6 * float(tfidf_similarity)
        except:
            pass
        
        # 2. Direct keyword matching (40% weight)
        course_words = set(course_text.lower().split())
        interest_words = set(interest_text.lower().split())
        
        # Count overlapping words
        overlap = len(course_words.intersection(interest_words))
        total_interest_words = len(interest_words)
        
        if total_interest_words > 0:
            keyword_score = min(overlap / total_interest_words, 1.0)
            score += 0.4 * keyword_score
        
        # Smart course boosting based on interest type
        for interest in interests:
            interest_lower = interest.lower()
            course_text_lower = f"{course.get('id', '')} {course.get('title', '')} {course.get('description', '')}".lower()
            
            # AI/ML boost (existing logic)
            if 'ai' in interest_lower or 'ml' in interest_lower:
                if self.is_ai_ml_course(course):
                    if course.get('id', '').startswith('CS') and any(term in course.get('title', '').lower() for term in ['artificial intelligence', 'machine learning']):
                        score += 0.8  # Maximum boost for core CS AI/ML courses
                    else:
                        score += 0.6  # Strong boost for other AI/ML courses
                elif score <= 0.1:  # Penalize completely irrelevant courses
                    score *= 0.3
            
            # Cybersecurity boost
            elif 'cyber' in interest_lower or 'security' in interest_lower:
                if any(term in course_text_lower for term in ['security', 'cyber', 'encryption', 'cryptography']):
                    if any(term in course_text_lower for term in ['cybersecurity', 'network security', 'information security']):
                        score += 0.7  # High boost for core security courses
                    else:
                        score += 0.4  # Moderate boost for security-related courses
            
            # UX Design boost - Extremely precise matching to avoid false positives
            elif 'ux' in interest_lower or 'design' in interest_lower:
                # Check for true UX course indicators
                is_true_ux = any(phrase in course_text_lower for phrase in [
                    'user experience', 'designing the user experience', 'discovering user needs',
                    'usability & measuring ux', 'user interface design', 'interaction design',
                    'human computer interaction', 'user research', 'user needs for ux'
                ])
                
                # Exclude courses that are clearly not UX
                is_false_positive = any(phrase in course_text_lower for phrase in [
                    'programming', 'linux', 'kernel', 'system administration', 'gpu',
                    'cluster programming', 'intensive programming', 'advanced topics'
                ])
                
                if is_true_ux and not is_false_positive:
                    score += 0.8  # Very strong boost for true UX courses only
                elif any(term in course_text_lower for term in ['human factors', 'ergonomics']) and not is_false_positive:
                    score += 0.4  # Moderate boost for human factors courses
            
            # Mechanical Engineering boost
            elif 'mechanical' in interest_lower:
                if any(term in course_text_lower for term in ['mechanical', 'manufacturing', 'design', 'cad', 'prototype']):
                    if 'mechanical' in course_text_lower or 'manufacturing' in course_text_lower:
                        score += 0.6  # Strong boost for mechanical courses
                    else:
                        score += 0.3  # Moderate boost for engineering design
            
            # Environmental Science boost
            elif 'environmental' in interest_lower:
                if any(term in course_text_lower for term in ['environmental', 'sustainability', 'remote sensing', 'gis']):
                    if 'environmental' in course_text_lower:
                        score += 0.6  # Strong boost for environmental courses
                    else:
                        score += 0.3  # Moderate boost for related courses
        
        return min(score, 1.0)  # Cap at 1.0
    
    def is_ai_ml_course(self, course: Dict) -> bool:
        """Detect if a course is clearly AI/ML related"""
        course_text = f"{course.get('id', '')} {course.get('title', '')} {course.get('description', '')} {course.get('topics', '')}".lower()
        
        # Strong AI/ML indicators
        ai_ml_keywords = [
            'artificial intelligence', 'machine learning', 'neural network', 'deep learning',
            'computer vision', 'natural language processing', 'data mining', 'robotics',
            'generative ai', 'ai', ' ml ', 'nlp', 'reinforcement learning', 'introduction to ai',
            'intro to ai', 'introduction to machine learning', 'intro to machine learning',
            'cs370', 'cs375', 'cs474', 'cs440', 'cs482',  # Specific course IDs
            'federated machine learning', 'ai for temporal', 'pattern recognition'
        ]
        
        # Must contain clear AI/ML keywords
        for keyword in ai_ml_keywords:
            if keyword in course_text:
                return True
        
        # Exclude false positives (courses that contain "machine" but aren't AI/ML)
        false_positives = [
            'machining', 'manual', 'welding', 'routing', 'manufacturing', 'mechanical'
        ]
        
        for false_pos in false_positives:
            if false_pos in course_text:
                return False
        
        return False
    
    def get_related_departments(self, department_filter: str, interests: List[str], 
                              specific_topics: str, career_goals: str) -> List[str]:
        """Determine related departments based on user interests and topics"""
        related_depts = [department_filter]  # Always include the selected department
        
        # Combine all user inputs to determine interests
        all_interests = ' '.join(interests + [specific_topics, career_goals]).lower()
        
        # AI/ML related interests
        if any(keyword in all_interests for keyword in [
            'ai', 'artificial intelligence', 'machine learning', 'neural', 'deep learning',
            'ml', 'data science', 'algorithm', 'generative'
        ]):
            related_depts.extend([
                'Computer Science', 'Data Science', 'Science Technology Society',
                'Engineering', 'Information Technology', 'Software and Data Engineering Technology'
            ])
        
        # Web development related interests  
        if any(keyword in all_interests for keyword in [
            'web', 'website', 'frontend', 'backend', 'javascript', 'html', 'css',
            'react', 'node', 'http', 'web development'
        ]):
            related_depts.extend([
                'Computer Science', 'Information Technology', 'Information Systems',
                'Software and Data Engineering Technology'
            ])
        
        # Data analysis/science related interests
        if any(keyword in all_interests for keyword in [
            'data', 'analytics', 'statistics', 'visualization', 'database',
            'sql', 'big data', 'pandas', 'python'
        ]):
            related_depts.extend([
                'Computer Science', 'Data Science', 'Information Systems',
                'Management Information Systems', 'Engineering'
            ])
        
        # Cybersecurity related interests
        if any(keyword in all_interests for keyword in [
            'security', 'cyber', 'encryption', 'network security', 'firewall',
            'hacking', 'cryptography', 'protection'
        ]):
            related_depts.extend([
                'Computer Science', 'Information Technology', 'Information Systems',
                'Engineering'
            ])
        
        # Mobile development related interests
        if any(keyword in all_interests for keyword in [
            'mobile', 'android', 'ios', 'app development', 'smartphone',
            'tablet', 'swift', 'kotlin'
        ]):
            related_depts.extend([
                'Computer Science', 'Information Technology', 'Information Systems',
                'Software and Data Engineering Technology'
            ])
        
        # Game development related interests
        if any(keyword in all_interests for keyword in [
            'game', 'gaming', 'unity', 'graphics', '3d', 'animation',
            'interactive', 'simulation'
        ]):
            related_depts.extend([
                'Computer Science', 'Information Technology'
            ])
        
        # Business/Management related interests
        if any(keyword in all_interests for keyword in [
            'business', 'management', 'entrepreneur', 'finance', 'marketing',
            'operations', 'accounting', 'economics'
        ]):
            related_depts.extend([
                'Management', 'Management Information Systems', 'Economics',
                'Entrepreneurship'
            ])
        
        # Design and UX related interests - PRIORITIZED ORDER
        if any(keyword in all_interests for keyword in [
            'design', 'ux', 'ui', 'user experience', 'user interface', 'usability',
            'interaction', 'user centered', 'user research', 'ergonomics', 'human factors'
        ]):
            # Priority order: most relevant departments first
            related_depts.extend([
                'Information Systems',  # Primary for UX courses
                'Computer Science', 'Information Technology', 
                'Engineering', 'Architecture'
            ])
        
        # Mechanical/Engineering related interests - EXPANDED
        if any(keyword in all_interests for keyword in [
            'mechanical', 'engineering design', 'manufacturing', 'systems design',
            'product design', 'cad', 'modeling', 'automation', 'robotics',
            'prototype', 'machining', 'assembly', 'tolerance', 'quality', 'reliability'
        ]):
            related_depts.extend([
                'Engineering',  # Primary for mechanical courses
                'Mechanical Engineering', 'Industrial Engineering',
                'Electrical Engineering', 'Computer Science'
            ])
        
        # Environmental/Science related interests - ENHANCED
        if any(keyword in all_interests for keyword in [
            'environmental', 'sustainability', 'ecology', 'climate', 'green',
            'conservation', 'gis', 'remote sensing', 'pollution', 'geographic',
            'spatial', 'water quality', 'air quality', 'environmental impact'
        ]):
            related_depts.extend([
                'Engineering',  # Primary for environmental courses
                'Science Technology Society', 'Computer Science',
                'Environmental Engineering', 'Civil Engineering'
            ])
        
        # Enhanced cybersecurity mapping - COMPREHENSIVE
        if any(keyword in all_interests for keyword in [
            'cybersecurity', 'security', 'cyber', 'encryption', 'firewall',
            'network security', 'information security', 'cryptography',
            'forensics', 'penetration', 'malware', 'compliance'
        ]):
            related_depts.extend([
                'Computer Science', 'Information Technology', 'Information Systems',
                'Engineering', 'Management'
            ])
        
        # Business Analytics & Data Science
        if any(keyword in all_interests for keyword in [
            'analytics', 'business intelligence', 'data warehouse', 'reporting'
        ]):
            related_depts.extend([
                'Management Information Systems', 'Computer Science', 'Data Science',
                'Management', 'Economics'
            ])
        
        # Psychology related interests
        if any(keyword in all_interests for keyword in [
            'psychology', 'psychological', 'behavior', 'cognitive', 'mental health',
            'human factors', 'social psychology', 'behavioral'
        ]):
            related_depts.extend([
                'Psychology', 'Science Technology Society', 'Engineering',
                'Information Systems'  # For human factors courses
            ])
        
        # Communication related interests
        if any(keyword in all_interests for keyword in [
            'communication', 'media', 'journalism', 'public relations',
            'broadcasting', 'digital media', 'marketing'
        ]):
            related_depts.extend([
                'Communication', 'Management', 'Information Systems',
                'Computer Science'  # For digital media courses
            ])
        
        # History/Humanities related interests
        if any(keyword in all_interests for keyword in [
            'history', 'humanities', 'culture', 'literature', 'philosophy',
            'anthropology', 'sociology', 'cultural studies'
        ]):
            related_depts.extend([
                'History', 'Literature', 'Philosophy', 'Science Technology Society',
                'Communication'  # For cultural media courses
            ])
        
        # Physics related interests
        if any(keyword in all_interests for keyword in [
            'physics', 'quantum', 'mechanics', 'thermodynamics', 'electromagnetism',
            'engineering physics', 'applied physics'
        ]):
            related_depts.extend([
                'Physics', 'Engineering', 'Electrical Engineering',
                'Mechanical Engineering', 'Computer Science'  # For computational physics
            ])
        
        # Theatre Arts related interests
        if any(keyword in all_interests for keyword in [
            'theatre', 'theater', 'performing arts', 'drama', 'production',
            'acting', 'performance', 'stage'
        ]):
            related_depts.extend([
                'Theatre', 'Communication', 'History',  # For theatre history
                'Literature'  # For dramatic literature
            ])
        
        # Health & Wellness related interests
        if any(keyword in all_interests for keyword in [
            'health', 'wellness', 'physical education', 'sports', 'fitness',
            'exercise', 'kinesiology', 'public health'
        ]):
            related_depts.extend([
                'Health & Physical Education', 'Biology', 'History',  # For health history
                'Environmental Science', 'Psychology'  # For health psychology
            ])
        
        # Science, Technology & Society related interests
        if any(keyword in all_interests for keyword in [
            'science technology society', 'sts', 'ethics', 'policy', 'innovation',
            'social impact', 'technology ethics'
        ]):
            related_depts.extend([
                'Science Technology Society', 'Philosophy', 'History',
                'Communication', 'Management'
            ])
        
        # Cloud/DevOps related interests
        if any(keyword in all_interests for keyword in [
            'cloud', 'aws', 'azure', 'devops', 'infrastructure', 'kubernetes',
            'docker', 'containerization', 'deployment'
        ]):
            related_depts.extend([
                'Computer Science', 'Information Technology', 'Information Systems',
                'Software and Data Engineering Technology'
            ])
        
        # Finance/Accounting related interests
        if any(keyword in all_interests for keyword in [
            'finance', 'accounting', 'financial', 'economics', 'investment',
            'financial analysis', 'financial modeling'
        ]):
            related_depts.extend([
                'Finance', 'Accounting', 'Economics', 'Management',
                'Management Information Systems'
            ])
        
        # Electrical Engineering related interests
        if any(keyword in all_interests for keyword in [
            'electrical', 'electronics', 'circuits', 'power', 'signal processing',
            'electrical engineering'
        ]):
            related_depts.extend([
                'Electrical Engineering', 'Engineering', 'Computer Science',
                'Physics'  # For electrical physics
            ])
        
        # Industrial Engineering related interests
        if any(keyword in all_interests for keyword in [
            'industrial', 'operations', 'supply chain', 'lean', 'six sigma',
            'industrial engineering', 'process improvement'
        ]):
            related_depts.extend([
                'Industrial Engineering', 'Engineering', 'Management',
                'Management Information Systems'
            ])
        
        # Remove duplicates and return
        return list(set(related_depts))
    
    def calculate_semantic_topic_score(self, course: Dict, specific_topics: str) -> float:
        """Enhanced semantic matching for specific topics with job description relevance"""
        if not specific_topics or not specific_topics.strip():
            return 0.5  # Neutral score if no specific topics
        
        # Get course content for matching
        course_content = f"{course.get('title', '')} {course.get('description', '')} {course.get('topics', '')} {course.get('career_relevance', '')}"
        course_content = self.preprocess_text(course_content)
        
        # Process user's specific topics
        topics_text = self.preprocess_text(specific_topics)
        
        if not course_content or not topics_text:
            return 0.5
        
        # Multi-layered semantic matching
        score = 0.0
        
        # 1. Direct TF-IDF similarity (40% weight)
        try:
            texts = [course_content, topics_text]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            tfidf_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            score += 0.4 * float(tfidf_similarity)
        except:
            pass
        
        # 2. Keyword overlap with synonyms (35% weight)
        course_words = set(course_content.lower().split())
        topic_words = set(topics_text.lower().split())
        
        # Expand with synonyms and related terms
        expanded_topics = set(topic_words)
        for topic in topic_words:
            # Add common synonyms for key terms
            if 'machin' in topic or 'ml' in topic:
                expanded_topics.update(['artifici', 'intellig', 'algorithm', 'neural', 'deep', 'learn'])
            elif 'web' in topic:
                expanded_topics.update(['html', 'css', 'javascript', 'frontend', 'backend', 'develop'])
            elif 'data' in topic:
                expanded_topics.update(['analysi', 'visual', 'statist', 'databas', 'sql'])
            elif 'secur' in topic:
                expanded_topics.update(['cybersecur', 'encrypt', 'network', 'attack', 'protect'])
            elif 'mobil' in topic:
                expanded_topics.update(['android', 'ios', 'app', 'develop'])
            elif 'financ' in topic:
                expanded_topics.update(['money', 'invest', 'bank', 'market', 'econom'])
        
        # Calculate enhanced overlap
        overlap = len(course_words.intersection(expanded_topics))
        if len(expanded_topics) > 0:
            keyword_score = min(overlap / len(expanded_topics), 1.0)
            score += 0.35 * keyword_score
        
        # 3. Phrase matching (25% weight) - look for exact phrases
        specific_lower = specific_topics.lower()
        course_lower = course_content.lower()
        
        # Extract meaningful phrases (2+ words)
        import re
        topic_phrases = re.findall(r'\b\w+\s+\w+(?:\s+\w+)*\b', specific_lower)
        phrase_matches = 0
        
        for phrase in topic_phrases:
            if len(phrase.split()) >= 2 and phrase in course_lower:
                phrase_matches += 1
        
        if len(topic_phrases) > 0:
            phrase_score = min(phrase_matches / len(topic_phrases), 1.0)
            score += 0.25 * phrase_score
        
        return min(score, 1.0)  # Cap at 1.0
    
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
    
    def calculate_level_appropriateness(self, course: Dict, completed_courses: List[str], academic_level: str = '') -> float:
        """Calculate how appropriate the course level is for the student"""
        level = course.get('level', '').lower()
        
        # Use provided academic level, fall back to estimating from completed courses
        if academic_level:
            student_level = academic_level.lower()
        else:
            # Estimate student level based on completed courses (fallback)
            num_completed = len(completed_courses)
            if num_completed == 0:
                student_level = 'freshman'
            elif num_completed < 5:
                student_level = 'sophomore'
            elif num_completed < 10:
                student_level = 'junior'
            else:
                student_level = 'senior'
        
        # Score based on level appropriateness
        if 'freshman' in level or 'intro' in level:
            if student_level == 'freshman':
                return 1.0  # Perfect match
            elif student_level == 'sophomore':
                return 0.8  # Still good
            elif student_level == 'junior':
                return 0.6  # Useful but less priority
            elif student_level == 'senior':
                return 0.4  # Lower priority for seniors
            else:
                return 0.7  # Graduate/unknown
        elif 'sophomore' in level:
            if student_level == 'freshman':
                return 0.7  # Accessible but slightly advanced
            elif student_level == 'sophomore':
                return 1.0  # Perfect match
            elif student_level == 'junior':
                return 0.8  # Still good
            elif student_level == 'senior':
                return 0.6  # Lower priority
            else:
                return 0.7  # Graduate/unknown
        elif 'junior' in level:
            if student_level == 'freshman':
                return 0.3  # Too advanced for freshmen
            elif student_level == 'sophomore':
                return 0.6  # Challenging but possible
            elif student_level == 'junior':
                return 1.0  # Perfect match
            elif student_level == 'senior':
                return 0.9  # Still very relevant
            else:
                return 0.8  # Graduate level
        elif 'senior' in level or 'graduate' in level:
            if student_level == 'freshman':
                return 0.1  # Way too advanced
            elif student_level == 'sophomore':
                return 0.2  # Still too advanced
            elif student_level == 'junior':
                return 0.5  # Challenging but doable
            elif student_level == 'senior':
                return 1.0  # Perfect match
            elif student_level == 'graduate':
                return 1.0  # Perfect for graduate students
            else:
                return 0.6  # Unknown level
        else:
            return 0.8  # Default for unknown course levels
    
    def calculate_course_level_bonus(self, course: Dict, academic_level: str) -> float:
        """Add bonus points for appropriate course number level"""
        if not academic_level:
            return 0.0  # No bonus if level unknown
        
        course_id = course.get('id', '')
        if len(course_id) < 5:
            return 0.0  # Invalid course ID
        
        try:
            # Extract course number (e.g., CS375 -> 375)
            course_num = int(course_id[2:5])
        except (ValueError, IndexError):
            return 0.0
        
        # Define preferred course levels for each academic level
        level_preferences = {
            'freshman': [100, 200],
            'sophomore': [200, 300],  # Sophomores should see 300-level courses!
            'junior': [300, 400],
            'senior': [400, 500],
            'graduate': [500, 600, 700]
        }
        
        preferred_levels = level_preferences.get(academic_level.lower(), [])
        
        # Give bonus for appropriate course level
        for level in preferred_levels:
            if level <= course_num < level + 100:
                # Higher bonus for more advanced students taking advanced courses
                if academic_level.lower() in ['sophomore', 'junior', 'senior'] and course_num >= 300:
                    return 0.15  # Strong bonus for advanced courses
                else:
                    return 0.10  # Standard bonus
        
        # Small penalty for courses that are too basic for advanced students
        if academic_level.lower() in ['junior', 'senior'] and course_num < 200:
            return -0.05  # Slight penalty for intro courses
        
        return 0.0  # No bonus/penalty
    
    def calculate_difficulty_score(self, course: Dict, difficulty_preference: str) -> float:
        """Calculate difficulty alignment score"""
        course_difficulty_raw = course.get('difficulty_rating', 3.0)
        
        # Map string difficulty ratings to numeric values
        difficulty_map = {
            'low': 2.0,
            'easy': 2.0,
            'medium': 3.5,
            'high': 4.5,
            'hard': 4.5,
            'any': 3.5
        }
        
        # Convert course difficulty to numeric if it's a string
        if isinstance(course_difficulty_raw, str):
            course_difficulty = difficulty_map.get(course_difficulty_raw.lower(), 3.5)
        else:
            course_difficulty = float(course_difficulty_raw)
        
        preferred_difficulty = difficulty_map.get(difficulty_preference.lower(), 3.5)
        
        # Calculate score based on how close the difficulties are
        diff = abs(course_difficulty - preferred_difficulty)
        score = max(0, 1 - (diff / 2.0))  # Normalize to 0-1 range
        
        return score
    
    def calculate_prerequisite_score(self, course: Dict, completed_courses: List[str]) -> float:
        """Check if student has completed prerequisites - more permissive for recommendations"""
        prerequisites = course.get('prerequisites', '')
        if not prerequisites or prerequisites.lower() in ['none', 'n/a']:
            return 1.0
        
        # Extract course codes from prerequisites string
        prereq_codes = re.findall(r'[A-Z]{2,4}\d{3}', prerequisites.upper())
        
        if not prereq_codes:
            # Check for standing/level prerequisites that shouldn't get full credit for beginners
            prereq_lower = prerequisites.lower()
            if any(standing in prereq_lower for standing in ['senior standing', 'senior', 'capstone']):
                return 0.2  # Still low for senior requirements but not crushing
            elif any(standing in prereq_lower for standing in ['junior standing', 'junior']):
                return 0.5  # More reasonable for junior requirements
            elif any(restriction in prereq_lower for restriction in ['majors only', 'restriction', 'approval']):
                return 0.8  # Minor penalty for restrictions
            else:
                return 1.0  # Other unparseable prerequisites (like general descriptions)
        
        completed_upper = [code.upper() for code in completed_courses]
        satisfied_count = sum(1 for prereq in prereq_codes if prereq in completed_upper)
        
        # Much more permissive scoring for aspirational learning:
        # - If no prerequisites completed: give 0.6 (aspirational learning)
        # - If some prerequisites completed: give good partial credit
        # - If all prerequisites completed: give full credit
        if len(prereq_codes) == 0:
            return 1.0
        elif satisfied_count == 0:
            return 0.6  # Encourage aspirational learning - show courses they can work toward
        else:
            # Partial credit: 0.6 base + 0.4 * completion ratio
            completion_ratio = satisfied_count / len(prereq_codes)
            return 0.6 + 0.4 * completion_ratio
    
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
    
    def get_recommendations(self, interests: List[str], specific_topics: str,
                          career_goals: str, preferred_topics: List[str], 
                          difficulty_preference: str = 'medium',
                          completed_courses: List[str] = None, num_recommendations: int = 10,
                          department_filter: str = '', include_cross_dept: bool = True,
                          academic_level: str = '') -> List[Dict]:
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
        
        # Determine which departments to include
        if include_cross_dept and department_filter:
            allowed_departments = self.get_related_departments(
                department_filter, interests, specific_topics, career_goals
            )
        else:
            allowed_departments = [department_filter] if department_filter else []
        
        # Calculate scores for each course
        recommendations = []
        
        for course in all_courses:
            # Skip if already completed
            if course['id'] in completed_courses:
                continue
            
            # Skip if department filter is applied and doesn't match allowed departments
            if department_filter and course.get('department', '') not in allowed_departments:
                continue
            
            # Hard filter: exclude manual machining and similar when AI/ML is selected
            if any('ai' in interest.lower() or 'ml' in interest.lower() for interest in interests):
                course_title = course.get('title', '').lower()
                if any(exclusion in course_title for exclusion in [
                    'manual machining', 'welding', 'cnc routing', 'physical metrology',
                    'remote sensing', 'technology society culture'
                ]):
                    continue
            
            # Calculate individual scores
            interest_score = self.calculate_interest_score(course, interests + preferred_topics)
            semantic_topic_score = self.calculate_semantic_topic_score(course, specific_topics)
            career_score = self.calculate_career_score(course, career_goals, is_exploring)
            difficulty_score = self.calculate_difficulty_score(course, difficulty_preference)
            prerequisite_score = self.calculate_prerequisite_score(course, completed_courses)
            popularity_score = self.calculate_popularity_score(course)
            level_appropriateness = self.calculate_level_appropriateness(course, completed_courses, academic_level)
            course_level_bonus = self.calculate_course_level_bonus(course, academic_level)
            
            # Smart Cross-Department Weighting with Topic Priority
            if include_cross_dept:
                # When cross-dept is ON: Heavily prioritize interest matching
                # Filter out courses with very low interest scores
                if interest_score < 0.2 and semantic_topic_score < 0.3:
                    continue  # Skip irrelevant courses
                
                # Dynamic weighting based on whether user provided specific topics
                has_specific_topics = specific_topics and specific_topics.strip()
                
                if has_specific_topics:
                    # User provided specific topics: PRIORITIZE semantic matching over interests
                    if is_exploring:
                        final_score = (
                            0.20 * interest_score +      # Reduced: Topics are more important
                            0.50 * semantic_topic_score + # MUCH HIGHER: Topics dominate
                            0.15 * career_score +        # Career focus
                            0.03 * difficulty_score +    # Lower
                            0.06 * prerequisite_score +  # Lower
                            0.02 * popularity_score +    # Lower
                            0.03 * level_appropriateness + # Lower
                            0.01 * (1 + course_level_bonus) # Lower
                        )
                    else:
                        final_score = (
                            0.25 * interest_score +      # Reduced: Topics more important
                            0.55 * semantic_topic_score + # HIGHEST: Topics are king
                            0.08 * career_score +        # Career alignment
                            0.02 * difficulty_score +    # Lower
                            0.05 * prerequisite_score +  # Lower
                            0.02 * popularity_score +    # Lower
                            0.02 * level_appropriateness + # Lower
                            0.01 * (1 + course_level_bonus) # Lower
                        )
                else:
                    # No specific topics: Original interest-focused weighting
                    if is_exploring:
                        final_score = (
                            0.40 * interest_score +      # MUCH HIGHER: Interest dominates
                            0.25 * semantic_topic_score + # Topic matching
                            0.15 * career_score +        # Career focus
                            0.04 * difficulty_score +    # Lower
                            0.08 * prerequisite_score +  # Lower
                            0.02 * popularity_score +    # Lower
                            0.04 * level_appropriateness + # Lower
                            0.02 * (1 + course_level_bonus) # Lower
                        )
                    else:
                        final_score = (
                            0.50 * interest_score +      # HIGHEST: Interest is king
                            0.25 * semantic_topic_score + # Topic matching
                            0.10 * career_score +        # Career alignment
                            0.03 * difficulty_score +    # Lower
                            0.06 * prerequisite_score +  # Lower
                            0.02 * popularity_score +    # Lower
                            0.03 * level_appropriateness + # Lower
                            0.01 * (1 + course_level_bonus) # Lower
                        )
            else:
                # Single department: Topic priority weighting
                has_specific_topics = specific_topics and specific_topics.strip()
                
                if has_specific_topics:
                    # User provided specific topics: PRIORITIZE semantic matching
                    if is_exploring:
                        final_score = (
                            0.05 * interest_score +      # Much lower: Topics are priority
                            0.45 * semantic_topic_score + # MUCH HIGHER: Topics dominate
                            0.20 * career_score +        # Career focus for exploration
                            0.05 * difficulty_score +    # Lower
                            0.12 * prerequisite_score +  # Lower
                            0.03 * popularity_score +    # Lower
                            0.08 * level_appropriateness + # Lower
                            0.02 * (1 + course_level_bonus) # Lower
                        )
                    else:
                        final_score = (
                            0.08 * interest_score +      # Much lower: Topics are priority
                            0.50 * semantic_topic_score + # HIGHEST: Topics are king
                            0.15 * career_score +        # Career alignment
                            0.05 * difficulty_score +    # Lower
                            0.10 * prerequisite_score +  # Lower
                            0.03 * popularity_score +    # Lower
                            0.07 * level_appropriateness + # Lower
                            0.02 * (1 + course_level_bonus) # Lower
                        )
                else:
                    # No specific topics: Original balanced weighting
                    if is_exploring:
                        final_score = (
                            0.10 * interest_score +      # Normal
                            0.25 * semantic_topic_score + # Topic matching
                            0.25 * career_score +        # Career focus for exploration
                            0.06 * difficulty_score +    # Normal
                            0.14 * prerequisite_score +  # Normal
                            0.04 * popularity_score +    # Normal
                            0.12 * level_appropriateness + # Normal
                            0.04 * (1 + course_level_bonus) # Normal
                        )
                    else:
                        final_score = (
                            0.15 * interest_score +      # Normal
                            0.30 * semantic_topic_score + # Topic matching
                            0.20 * career_score +        # Career alignment
                            0.06 * difficulty_score +    # Normal
                            0.14 * prerequisite_score +  # Normal
                            0.04 * popularity_score +    # Normal
                            0.08 * level_appropriateness + # Normal
                            0.03 * (1 + course_level_bonus) # Normal
                        )

            # CRITICAL: Smart final boost that respects user priorities
            # Priority order: 1) Specific topics (user's detailed input), 2) General interests
            has_specific_topics = specific_topics and specific_topics.strip()
            
            # DIRECT TOPIC MATCHING BOOST (when user provides specific topics)
            if has_specific_topics:
                topic_keywords = specific_topics.lower().split()
                course_text_for_topics = f"{course.get('id', '')} {course.get('title', '')} {course.get('description', '')}".lower()
                
                # Direct keyword matching for common topic areas
                topic_boost = 0.0
                
                # Web development boost
                if any(term in specific_topics.lower() for term in ['web', 'html', 'css', 'javascript', 'website', 'frontend', 'backend']):
                    if any(term in course_text_for_topics for term in ['web', 'website', 'html', 'internet applications', 'web applications']):
                        topic_boost += 0.4  # Strong boost for web courses when web topics specified
                
                # AI/ML topic boost
                elif any(term in specific_topics.lower() for term in ['artificial intelligence', 'machine learning', 'neural', 'ai', 'ml']):
                    if any(term in course_text_for_topics for term in ['artificial intelligence', 'machine learning', 'ai', 'neural', 'data science']):
                        topic_boost += 0.4  # Strong boost for AI courses when AI topics specified
                
                # Data science topic boost
                elif any(term in specific_topics.lower() for term in ['data science', 'analytics', 'visualization', 'statistics']):
                    if any(term in course_text_for_topics for term in ['data science', 'analytics', 'data analysis', 'statistics']):
                        topic_boost += 0.4  # Strong boost for data courses when data topics specified
                
                # Security topic boost  
                elif any(term in specific_topics.lower() for term in ['security', 'cybersecurity', 'encryption', 'cryptography']):
                    if any(term in course_text_for_topics for term in ['security', 'cybersecurity', 'encryption', 'cryptography']):
                        topic_boost += 0.4  # Strong boost for security courses when security topics specified
                
                # Apply the topic boost
                if topic_boost > 0:
                    final_score += topic_boost
            
            # INTEREST-BASED BOOSTS (lower priority when specific topics provided)
            for interest in interests:
                interest_lower = interest.lower()
                course_text_lower = f"{course.get('id', '')} {course.get('title', '')} {course.get('description', '')}".lower()
                
                # If user provided specific topics, reduce interest boost to let topics dominate
                if has_specific_topics:
                    interest_boost = 0.08  # Much reduced boost when user has specific topics
                else:
                    interest_boost = 0.25  # Full boost when only general interests provided
                
                # Apply boost for perfect matches (strength depends on user input specificity)
                boost_applied = False
                
                # AI/ML courses
                if ('ai' in interest_lower or 'ml' in interest_lower or 'machine' in interest_lower) and not boost_applied:
                    if self.is_ai_ml_course(course):
                        final_score += interest_boost  # Dynamic boost based on user input specificity
                        boost_applied = True
                
                # UX Design courses - Very precise matching to avoid false positives like CS288
                elif ('ux' in interest_lower or 'design' in interest_lower) and not boost_applied:
                    # Only boost if it's clearly a UX course (strict criteria)
                    is_true_ux_course = any(phrase in course_text_lower for phrase in [
                        'user experience', 'designing the user experience', 'discovering user needs',
                        'usability & measuring ux', 'user interface design', 'interaction design',
                        'human computer interaction', 'user research', 'user needs for ux'
                    ])
                    
                    # Exclude courses that are clearly not UX despite having "user" in the title
                    is_false_positive = any(phrase in course_text_lower for phrase in [
                        'programming', 'linux', 'kernel', 'system administration', 'gpu',
                        'cluster programming', 'security', 'cryptography', 'networking'
                    ])
                    
                    if is_true_ux_course and not is_false_positive:
                        final_score += interest_boost  # Dynamic boost for true UX courses
                        boost_applied = True
                
                # Cybersecurity courses
                elif ('cyber' in interest_lower or 'security' in interest_lower) and not boost_applied:
                    if any(term in course_text_lower for term in ['cybersecurity', 'network security', 'information security', 'encryption', 'cryptography']):
                        final_score += interest_boost  # Dynamic boost for cybersecurity
                        boost_applied = True
                
                # Mechanical Engineering courses
                elif 'mechanical' in interest_lower and not boost_applied:
                    if any(term in course_text_lower for term in ['mechanical', 'manufacturing', 'prototyping', 'machining', 'production']):
                        final_score += interest_boost  # Dynamic boost for mechanical
                        boost_applied = True
                
                # Environmental Science courses
                elif 'environmental' in interest_lower and not boost_applied:
                    if any(term in course_text_lower for term in ['environmental', 'sustainability', 'remote sensing', 'ecology', 'climate']):
                        final_score += interest_boost  # Dynamic boost for environmental
                        boost_applied = True
                
                # Web Development courses
                elif 'web' in interest_lower and not boost_applied:
                    if any(term in course_text_lower for term in ['web', 'website', 'html', 'css', 'javascript', 'internet applications']):
                        final_score += interest_boost  # Dynamic boost for web development
                        boost_applied = True
                
                # Data Science courses
                elif 'data' in interest_lower and not boost_applied:
                    if any(term in course_text_lower for term in ['data science', 'data analytics', 'statistics', 'visualization']):
                        final_score += interest_boost  # Dynamic boost for data science
                        boost_applied = True
                
                # Mobile Development courses
                elif 'mobile' in interest_lower and not boost_applied:
                    if any(term in course_text_lower for term in ['mobile', 'android', 'ios', 'app development']):
                        final_score += interest_boost  # Dynamic boost for mobile development
                        boost_applied = True
                
                # Game Development courses
                elif 'game' in interest_lower and not boost_applied:
                    if any(term in course_text_lower for term in ['game', 'gaming', 'unity', 'graphics', '3d']):
                        final_score += interest_boost  # Dynamic boost for game development
                        boost_applied = True
                
                # Psychology courses
                elif 'psychology' in interest_lower and not boost_applied:
                    if any(term in course_text_lower for term in ['psychology', 'psychological', 'behavior', 'cognitive', 'mental health', 'human factors']):
                        final_score += interest_boost * 3.2  # Strong boost matching AI/ML level
                        boost_applied = True
                
                # Communication courses
                elif 'communication' in interest_lower and not boost_applied:
                    if any(term in course_text_lower for term in ['communication', 'media', 'journalism', 'public relations', 'broadcasting', 'digital media']):
                        final_score += interest_boost * 3.2  # Strong boost matching AI/ML level
                        boost_applied = True
                
                # Science, Technology & Society courses
                elif ('science technology society' in interest_lower or 'sts' in interest_lower) and not boost_applied:
                    if any(term in course_text_lower for term in ['science technology society', 'sts', 'ethics', 'policy', 'innovation', 'social impact']):
                        final_score += interest_boost * 3.2  # Strong boost matching AI/ML level
                        boost_applied = True
                
                # Physics courses
                elif 'physics' in interest_lower and not boost_applied:
                    if any(term in course_text_lower for term in ['physics', 'quantum', 'mechanics', 'thermodynamics', 'electromagnetism']):
                        final_score += interest_boost * 3.2  # Strong boost matching AI/ML level
                        boost_applied = True
                
                # History/Humanities courses
                elif ('history' in interest_lower or 'humanities' in interest_lower) and not boost_applied:
                    if any(term in course_text_lower for term in ['history', 'humanities', 'culture', 'literature', 'philosophy', 'anthropology']):
                        final_score += interest_boost * 3.2  # Strong boost matching AI/ML level
                        boost_applied = True
                
                # Theatre Arts courses
                elif 'theatre' in interest_lower and not boost_applied:
                    if any(term in course_text_lower for term in ['theatre', 'theater', 'performing arts', 'drama', 'production', 'acting']):
                        final_score += interest_boost * 3.2  # Strong boost matching AI/ML level
                        boost_applied = True
                
                # Health & Wellness courses
                elif ('health' in interest_lower or 'wellness' in interest_lower) and not boost_applied:
                    if any(term in course_text_lower for term in ['health', 'wellness', 'physical education', 'sports', 'fitness', 'exercise']):
                        final_score += interest_boost * 3.2  # Strong boost matching AI/ML level
                        boost_applied = True
                
                # Cloud/DevOps courses
                elif ('cloud' in interest_lower or 'devops' in interest_lower) and not boost_applied:
                    if any(term in course_text_lower for term in ['cloud', 'aws', 'azure', 'devops', 'infrastructure', 'kubernetes']):
                        final_score += interest_boost * 3.2  # Strong boost matching AI/ML level
                        boost_applied = True
                
                # Finance/Accounting courses
                elif ('finance' in interest_lower or 'accounting' in interest_lower) and not boost_applied:
                    if any(term in course_text_lower for term in ['finance', 'accounting', 'financial', 'economics', 'investment']):
                        final_score += interest_boost * 3.2  # Strong boost matching AI/ML level
                        boost_applied = True
                
                # Electrical Engineering courses
                elif 'electrical' in interest_lower and not boost_applied:
                    if any(term in course_text_lower for term in ['electrical', 'electronics', 'circuits', 'power', 'signal processing']):
                        final_score += interest_boost * 3.2  # Strong boost matching AI/ML level
                        boost_applied = True
                
                # Industrial Engineering courses
                elif 'industrial' in interest_lower and not boost_applied:
                    if any(term in course_text_lower for term in ['industrial', 'operations', 'supply chain', 'lean', 'six sigma']):
                        final_score += interest_boost * 3.2  # Strong boost matching AI/ML level
                        boost_applied = True
                
                # Moderate boost for partially relevant courses (also dynamic)
                if not boost_applied and interest_score >= 0.4:
                    final_score += interest_boost * 0.4  # Proportional boost for good interest match

            
            # Add recommendation with detailed scoring
            recommendation = {
                **course,
                'recommendation_score': round(final_score, 3),
                'score_breakdown': {
                    'interest_match': round(interest_score, 3),
                    'semantic_topic_match': round(semantic_topic_score, 3),
                    'career_alignment': round(career_score, 3),
                    'difficulty_fit': round(difficulty_score, 3),
                    'prerequisites_met': round(prerequisite_score, 3),
                    'popularity': round(popularity_score, 3),
                    'level_appropriateness': round(level_appropriateness, 3),
                    'course_level_bonus': round(course_level_bonus, 3)
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