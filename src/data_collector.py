import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from typing import List, Dict
import time

class NJITDataCollector:
    """
    Utility class for collecting NJIT course data from various sources
    """
    
    def __init__(self):
        self.base_url = "https://catalog.njit.edu"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def create_sample_csv(self, filename="data/njit_courses.csv"):
        """Create a sample CSV file with NJIT course data that users can modify"""
        
        sample_data = [
            {
                "id": "CS490",
                "title": "Guided Design in Software Engineering",
                "description": "Capstone course focusing on software engineering principles, team collaboration, and real-world project development. Students work in teams to develop substantial software systems.",
                "credits": 3,
                "prerequisites": "CS280, CS288",
                "department": "Computer Science",
                "level": "Senior",
                "difficulty_rating": 4.2,
                "career_relevance": "Software Development, Project Management, Team Leadership, Systems Architecture",
                "topics": "Software Engineering, Project Management, Team Collaboration, System Design, Agile Development",
                "semester_offered": "Fall, Spring",
                "professor": "Various Faculty",
                "rating": 4.1,
                "enrollment_count": 120
            },
            {
                "id": "CS485",
                "title": "Computer Security",
                "description": "Introduction to computer security including cryptography, network security, system vulnerabilities, and ethical hacking principles.",
                "credits": 3,
                "prerequisites": "CS280, CS356",
                "department": "Computer Science",
                "level": "Senior",
                "difficulty_rating": 4.0,
                "career_relevance": "Cybersecurity, Information Security, Security Engineering, Penetration Testing",
                "topics": "Cryptography, Network Security, Vulnerability Assessment, Ethical Hacking, Security Protocols",
                "semester_offered": "Fall, Spring",
                "professor": "Dr. Smith",
                "rating": 4.3,
                "enrollment_count": 85
            },
            {
                "id": "CS435",
                "title": "Advanced Data Structures and Algorithms",
                "description": "Advanced topics in data structures and algorithm analysis including graph algorithms, dynamic programming, and optimization techniques.",
                "credits": 3,
                "prerequisites": "CS280, CS341",
                "department": "Computer Science",
                "level": "Senior",
                "difficulty_rating": 4.5,
                "career_relevance": "Software Engineering, Algorithm Development, Technical Interviews, Research",
                "topics": "Graph Algorithms, Dynamic Programming, Optimization, Algorithm Analysis, Complexity Theory",
                "semester_offered": "Fall",
                "professor": "Dr. Johnson",
                "rating": 4.2,
                "enrollment_count": 75
            },
            {
                "id": "CS480",
                "title": "Introduction to Machine Learning",
                "description": "Fundamentals of machine learning including supervised and unsupervised learning algorithms, neural networks, and practical applications.",
                "credits": 3,
                "prerequisites": "CS280, MATH333",
                "department": "Computer Science",
                "level": "Senior",
                "difficulty_rating": 4.3,
                "career_relevance": "Data Science, AI Engineering, Machine Learning Engineer, Research Scientist",
                "topics": "Supervised Learning, Unsupervised Learning, Neural Networks, Data Mining, Pattern Recognition",
                "semester_offered": "Fall, Spring",
                "professor": "Dr. Chen",
                "rating": 4.4,
                "enrollment_count": 95
            },
            {
                "id": "CS656",
                "title": "Internet and Higher Layer Protocols",
                "description": "Advanced study of internet protocols, network architecture, distributed systems, and performance analysis.",
                "credits": 3,
                "prerequisites": "CS356",
                "department": "Computer Science",
                "level": "Graduate",
                "difficulty_rating": 4.1,
                "career_relevance": "Network Engineering, Systems Architecture, Cloud Computing, DevOps",
                "topics": "Network Protocols, Distributed Systems, Cloud Architecture, Performance Analysis, Scalability",
                "semester_offered": "Spring",
                "professor": "Dr. Wilson",
                "rating": 4.0,
                "enrollment_count": 45
            },
            {
                "id": "CS643",
                "title": "Web Mining",
                "description": "Techniques for mining and analyzing web data including web crawling, information extraction, and search engine technologies.",
                "credits": 3,
                "prerequisites": "CS280, CS480",
                "department": "Computer Science",
                "level": "Graduate",
                "difficulty_rating": 3.8,
                "career_relevance": "Data Science, Web Analytics, Search Engineering, Business Intelligence",
                "topics": "Web Crawling, Information Extraction, Search Engines, Web Analytics, Data Mining",
                "semester_offered": "Fall",
                "professor": "Dr. Martinez",
                "rating": 4.1,
                "enrollment_count": 55
            },
            {
                "id": "CS634",
                "title": "Data Mining",
                "description": "Techniques and algorithms for discovering patterns in large datasets, including classification, clustering, and association rules.",
                "credits": 3,
                "prerequisites": "CS280, MATH333",
                "department": "Computer Science",
                "level": "Graduate",
                "difficulty_rating": 4.0,
                "career_relevance": "Data Science, Business Analytics, Research, Machine Learning Engineering",
                "topics": "Classification, Clustering, Association Rules, Feature Selection, Big Data Analytics",
                "semester_offered": "Spring",
                "professor": "Dr. Lee",
                "rating": 4.2,
                "enrollment_count": 60
            },
            {
                "id": "CS631",
                "title": "Data Management System Design",
                "description": "Advanced database concepts including query optimization, transaction processing, and distributed database systems.",
                "credits": 3,
                "prerequisites": "CS280, CS482",
                "department": "Computer Science",
                "level": "Graduate",
                "difficulty_rating": 4.2,
                "career_relevance": "Database Administration, Systems Engineering, Backend Development, Data Architecture",
                "topics": "Query Optimization, Transaction Processing, Distributed Databases, NoSQL, Database Tuning",
                "semester_offered": "Fall",
                "professor": "Dr. Brown",
                "rating": 3.9,
                "enrollment_count": 50
            },
            {
                "id": "CS675",
                "title": "Introduction to Computer Graphics",
                "description": "Fundamentals of computer graphics including 2D/3D transformations, rendering algorithms, and interactive graphics programming.",
                "credits": 3,
                "prerequisites": "CS280, MATH333",
                "department": "Computer Science",
                "level": "Graduate",
                "difficulty_rating": 3.9,
                "career_relevance": "Game Development, Computer Graphics, UI/UX Design, Simulation",
                "topics": "3D Graphics, Rendering, Animation, Shaders, Graphics Programming",
                "semester_offered": "Fall",
                "professor": "Dr. Garcia",
                "rating": 4.3,
                "enrollment_count": 40
            },
            {
                "id": "CS670",
                "title": "Artificial Intelligence",
                "description": "Introduction to artificial intelligence including search algorithms, knowledge representation, expert systems, and AI applications.",
                "credits": 3,
                "prerequisites": "CS280, CS341",
                "department": "Computer Science",
                "level": "Graduate",
                "difficulty_rating": 4.1,
                "career_relevance": "AI Engineering, Robotics, Expert Systems, Intelligent Systems Development",
                "topics": "Search Algorithms, Knowledge Representation, Expert Systems, Planning, AI Ethics",
                "semester_offered": "Spring",
                "professor": "Dr. Kim",
                "rating": 4.2,
                "enrollment_count": 70
            }
        ]
        
        # Ensure data directory exists
        import os
        os.makedirs("data", exist_ok=True)
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(sample_data)
        df.to_csv(filename, index=False)
        print(f"Sample course data created: {filename}")
        print(f"You can edit this CSV file to add more NJIT courses or modify existing ones.")
        
        return filename
    
    def create_data_template(self):
        """Create a template for manual data entry"""
        template = {
            "instructions": "Fill out this template for each NJIT elective course",
            "course_template": {
                "id": "CS###",
                "title": "Course Title",
                "description": "Detailed course description covering topics and learning objectives",
                "credits": 3,
                "prerequisites": "List of prerequisite courses (e.g., CS280, MATH333)",
                "department": "Computer Science | Information Systems | etc.",
                "level": "Undergraduate | Graduate | Senior",
                "difficulty_rating": "Scale 1-5 (1=Easy, 5=Very Hard)",
                "career_relevance": "Comma-separated career paths this course supports",
                "topics": "Comma-separated list of key topics covered",
                "semester_offered": "Fall | Spring | Summer | Fall, Spring",
                "professor": "Professor name or 'Various'",
                "rating": "Average student rating 1-5",
                "enrollment_count": "Typical enrollment number"
            }
        }
        
        with open("data/course_template.json", "w") as f:
            json.dump(template, f, indent=2)
        
        print("Course template created: data/course_template.json")
        return "data/course_template.json"
    
    def scrape_njit_catalog(self):
        """
        Placeholder for web scraping NJIT course catalog
        This would need to be customized based on NJIT's actual website structure
        """
        print("Web scraping functionality would be implemented here.")
        print("This requires analyzing NJIT's course catalog website structure.")
        print("For now, please use the CSV template or manual data entry.")
        
        # Example structure for reference:
        return {
            "status": "not_implemented",
            "suggestion": "Use create_sample_csv() method to get started with sample data"
        }