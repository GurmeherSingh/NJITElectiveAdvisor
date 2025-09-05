import sqlite3
import pandas as pd
import json
import os
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

class DataManager:
    def __init__(self, db_path="data/courses.db"):
        self.db_path = db_path
        self.ensure_data_directory()
        self.init_database()
        
        # Check if departments table is empty and populate if needed
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        conn.close()
        
        if dept_count == 0:
            self.load_departments()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create courses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                credits INTEGER,
                prerequisites TEXT,
                department TEXT,
                level TEXT,
                difficulty_rating REAL,
                career_relevance TEXT,
                topics TEXT,
                semester_offered TEXT,
                professor TEXT,
                rating REAL,
                enrollment_count INTEGER,
                avg_rating REAL DEFAULT 0.0,
                total_ratings INTEGER DEFAULT 0
            )
        ''')
        
        # Create student preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                interests TEXT,
                career_goals TEXT,
                preferred_topics TEXT,
                difficulty_preference TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                course_id TEXT,
                rating INTEGER,
                helpful BOOLEAN,
                comments TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                student_id TEXT UNIQUE,
                major TEXT,
                academic_level TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create saved_courses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id TEXT NOT NULL,
                saved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (course_id) REFERENCES courses (id),
                UNIQUE(user_id, course_id)
            )
        ''')
        
        # Create student_ratings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_email TEXT NOT NULL,
                course_id TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                review TEXT,
                completed_semester TEXT,
                would_recommend BOOLEAN DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses (id),
                UNIQUE(student_email, course_id)
            )
        ''')
        
        # Create departments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                full_name TEXT,
                description TEXT,
                website TEXT,
                contact_email TEXT,
                total_courses INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_sample_data(self):
        """Load sample NJIT course data"""
        sample_courses = [
            {
                "id": "CS490",
                "title": "Guided Design in Software Engineering",
                "description": "Capstone course focusing on software engineering principles, team collaboration, and real-world project development.",
                "credits": 3,
                "prerequisites": "CS280, CS288",
                "department": "Computer Science",
                "level": "Senior",
                "difficulty_rating": 4.2,
                "career_relevance": "Software Development, Project Management, Team Leadership",
                "topics": "Software Engineering, Project Management, Team Collaboration, System Design",
                "semester_offered": "Fall, Spring",
                "professor": "Various",
                "rating": 4.1
            },
            {
                "id": "CS485",
                "title": "Computer Security",
                "description": "Introduction to computer security including cryptography, network security, and system vulnerabilities.",
                "credits": 3,
                "prerequisites": "CS280, CS356",
                "department": "Computer Science",
                "level": "Senior",
                "difficulty_rating": 4.0,
                "career_relevance": "Cybersecurity, Information Security, Security Engineering",
                "topics": "Cryptography, Network Security, Vulnerability Assessment, Ethical Hacking",
                "semester_offered": "Fall, Spring",
                "professor": "Dr. Smith",
                "rating": 4.3
            },
            {
                "id": "CS435",
                "title": "Advanced Data Structures and Algorithms",
                "description": "Advanced topics in data structures and algorithm analysis including graph algorithms and optimization techniques.",
                "credits": 3,
                "prerequisites": "CS280, CS341",
                "department": "Computer Science",
                "level": "Senior",
                "difficulty_rating": 4.5,
                "career_relevance": "Software Engineering, Algorithm Development, Technical Interviews",
                "topics": "Graph Algorithms, Dynamic Programming, Optimization, Algorithm Analysis",
                "semester_offered": "Fall",
                "professor": "Dr. Johnson",
                "rating": 4.2
            },
            {
                "id": "CS480",
                "title": "Introduction to Machine Learning",
                "description": "Fundamentals of machine learning including supervised and unsupervised learning algorithms.",
                "credits": 3,
                "prerequisites": "CS280, MATH333",
                "department": "Computer Science",
                "level": "Senior",
                "difficulty_rating": 4.3,
                "career_relevance": "Data Science, AI Engineering, Machine Learning Engineer",
                "topics": "Supervised Learning, Unsupervised Learning, Neural Networks, Data Mining",
                "semester_offered": "Fall, Spring",
                "professor": "Dr. Chen",
                "rating": 4.4
            },
            {
                "id": "CS656",
                "title": "Internet and Higher Layer Protocols",
                "description": "Study of internet protocols, network architecture, and distributed systems.",
                "credits": 3,
                "prerequisites": "CS356",
                "department": "Computer Science",
                "level": "Graduate",
                "difficulty_rating": 4.1,
                "career_relevance": "Network Engineering, Systems Architecture, Cloud Computing",
                "topics": "Network Protocols, Distributed Systems, Cloud Architecture, Performance Analysis",
                "semester_offered": "Spring",
                "professor": "Dr. Wilson",
                "rating": 4.0
            },
            {
                "id": "CS643",
                "title": "Web Mining",
                "description": "Techniques for mining and analyzing web data including web crawling and information extraction.",
                "credits": 3,
                "prerequisites": "CS280, CS480",
                "department": "Computer Science",
                "level": "Graduate",
                "difficulty_rating": 3.8,
                "career_relevance": "Data Science, Web Analytics, Search Engineering",
                "topics": "Web Crawling, Information Extraction, Search Engines, Web Analytics",
                "semester_offered": "Fall",
                "professor": "Dr. Martinez",
                "rating": 4.1
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        for course in sample_courses:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO courses 
                (id, title, description, credits, prerequisites, department, 
                 level, difficulty_rating, career_relevance, topics, 
                 semester_offered, professor, avg_rating, total_ratings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                course["id"], course["title"], course["description"], 
                course["credits"], course["prerequisites"], course["department"],
                course["level"], course["difficulty_rating"], course["career_relevance"],
                course["topics"], course["semester_offered"], course["professor"],
                course.get("rating", 0), 0
            ))
        conn.commit()
        conn.close()
        
        print(f"Loaded {len(sample_courses)} sample courses into database")
    
    def load_departments(self):
        """Load NJIT departments into database"""
        departments = [
            {"id": "CS", "name": "Computer Science", "full_name": "Computer Science Department"},
            {"id": "ECE", "name": "Electrical & Computer Engineering", "full_name": "Electrical & Computer Engineering Department"},
            {"id": "ME", "name": "Mechanical Engineering", "full_name": "Mechanical Engineering Department"},
            {"id": "CE", "name": "Civil Engineering", "full_name": "Civil Engineering Department"},
            {"id": "CHE", "name": "Chemical Engineering", "full_name": "Chemical Engineering Department"},
            {"id": "BME", "name": "Biomedical Engineering", "full_name": "Biomedical Engineering Department"},
            {"id": "MATH", "name": "Mathematics", "full_name": "Mathematical Sciences Department"},
            {"id": "PHYS", "name": "Physics", "full_name": "Physics Department"},
            {"id": "CHEM", "name": "Chemistry", "full_name": "Chemistry & Environmental Science Department"},
            {"id": "BIOL", "name": "Biology", "full_name": "Biological Sciences Department"},
            {"id": "MGMT", "name": "Management", "full_name": "School of Management"},
            {"id": "FIN", "name": "Finance", "full_name": "Finance Department"},
            {"id": "ACCT", "name": "Accounting", "full_name": "Accounting Department"},
            {"id": "MIS", "name": "Management Information Systems", "full_name": "Management Information Systems Department"},
            {"id": "IS", "name": "Information Systems", "full_name": "Information Systems Department"},
            {"id": "IT", "name": "Information Technology", "full_name": "Information Technology Department"},
            {"id": "DS", "name": "Data Science", "full_name": "Data Science Department"},
            {"id": "ARCH", "name": "Architecture", "full_name": "School of Architecture"},
            {"id": "ARTD", "name": "Art & Design", "full_name": "Art & Design Department"},
            {"id": "ENG", "name": "English", "full_name": "Humanities Department"},
            {"id": "SLA", "name": "Science, Liberal Arts", "full_name": "Science, Liberal Arts Department"}
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for dept in departments:
            cursor.execute('''
                INSERT OR REPLACE INTO departments (id, name, full_name)
                VALUES (?, ?, ?)
            ''', (dept["id"], dept["name"], dept["full_name"]))
        
        conn.commit()
        conn.close()
        
        print(f"Loaded {len(departments)} departments into database")
    
    def scrape_njit_courses(self):
        """
        Scrape course information from NJIT website
        This is a template - you'll need to adapt based on NJIT's actual website structure
        """
        print("Web scraping functionality - requires NJIT course catalog URL structure")
        # TODO: Implement based on actual NJIT course catalog structure
        pass
    
    def import_courses_from_csv(self, csv_path: str):
        """Import courses from a CSV file"""
        try:
            df = pd.read_csv(csv_path)
            conn = sqlite3.connect(self.db_path)
            df.to_sql('courses', conn, if_exists='append', index=False)
            conn.close()
            print(f"Successfully imported {len(df)} courses from {csv_path}")
        except Exception as e:
            print(f"Error importing CSV: {e}")
    
    def get_all_courses(self) -> List[Dict]:
        """Get all courses from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses")
        columns = [description[0] for description in cursor.description]
        courses = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return courses
    
    def get_course_by_id(self, course_id: str) -> Optional[Dict]:
        """Get specific course by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        row = cursor.fetchone()
        if row:
            columns = [description[0] for description in cursor.description]
            course = dict(zip(columns, row))
        else:
            course = None
        conn.close()
        return course
    
    def search_courses(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search courses based on query and filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = """
            SELECT * FROM courses 
            WHERE (title LIKE ? OR description LIKE ? OR topics LIKE ? OR career_relevance LIKE ?)
        """
        params = [f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"]
        
        if filters:
            if 'department' in filters:
                sql += " AND department = ?"
                params.append(filters['department'])
            if 'level' in filters:
                sql += " AND level = ?"
                params.append(filters['level'])
            if 'max_difficulty' in filters:
                sql += " AND difficulty_rating <= ?"
                params.append(filters['max_difficulty'])
        
        cursor.execute(sql, params)
        columns = [description[0] for description in cursor.description]
        courses = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return courses
    
    def get_course_statistics(self) -> Dict:
        """Get statistics about the course database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM courses")
        total_courses = cursor.fetchone()[0]
        
        cursor.execute("SELECT department, COUNT(*) FROM courses GROUP BY department")
        departments = dict(cursor.fetchall())
        
        cursor.execute("SELECT AVG(difficulty_rating), AVG(avg_rating) FROM courses")
        avg_difficulty, avg_rating = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_courses": total_courses,
            "departments": departments,
            "average_difficulty": round(avg_difficulty, 2) if avg_difficulty else 0,
            "average_rating": round(avg_rating, 2) if avg_rating else 0
        }
    
    def add_student_rating(self, rating_data: Dict) -> bool:
        """Add a student rating for a course"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert rating
            cursor.execute('''
                INSERT OR REPLACE INTO student_ratings 
                (student_email, course_id, rating, review, completed_semester, would_recommend)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                rating_data['student_email'],
                rating_data['course_id'],
                rating_data['rating'],
                rating_data['review'],
                rating_data['completed_semester'],
                rating_data['would_recommend']
            ))
            
            # Update course average rating
            cursor.execute('''
                SELECT AVG(rating), COUNT(rating) FROM student_ratings 
                WHERE course_id = ?
            ''', (rating_data['course_id'],))
            
            avg_rating, total_ratings = cursor.fetchone()
            
            cursor.execute('''
                UPDATE courses 
                SET avg_rating = ?, total_ratings = ?
                WHERE id = ?
            ''', (round(avg_rating, 2), total_ratings, rating_data['course_id']))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding rating: {e}")
            return False
    
    def get_course_ratings(self, course_id: str) -> List[Dict]:
        """Get all ratings for a specific course"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT student_email, rating, review, completed_semester, would_recommend, timestamp
            FROM student_ratings 
            WHERE course_id = ?
            ORDER BY timestamp DESC
        ''', (course_id,))
        
        columns = ['student_email', 'rating', 'review', 'completed_semester', 'would_recommend', 'timestamp']
        ratings = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return ratings
    
    def get_course_average_rating(self, course_id: str) -> float:
        """Get the average rating for a course"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT avg_rating FROM courses WHERE id = ?", (course_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else 0.0
    
    def get_all_departments(self) -> List[Dict]:
        """Get all departments from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM departments")
        columns = [description[0] for description in cursor.description]
        departments = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return departments
    
    # User Management Methods
    def create_user(self, email: str, password_hash: str, first_name: str, last_name: str, 
                   student_id: Optional[str] = None, major: Optional[str] = None, 
                   academic_level: Optional[str] = None) -> Optional[int]:
        """Create a new user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name, student_id, major, academic_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (email, password_hash, first_name, last_name, student_id, major, academic_level))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
            
        except sqlite3.IntegrityError as e:
            print(f"User creation failed: {e}")
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email address"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row  # Enable row factory for better error handling
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = 1', (email,))
            user_data = cursor.fetchone()
            
            if user_data:
                return dict(user_data)
            return None
        except sqlite3.OperationalError as e:
            print(f"Database operational error getting user by email: {e}")
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row  # Enable row factory for better error handling
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE id = ? AND is_active = 1', (user_id,))
            user_data = cursor.fetchone()
            
            if user_data:
                return dict(user_data)
            return None
        except sqlite3.OperationalError as e:
            print(f"Database operational error getting user by ID: {e}")
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
            conn.commit()
            return True
            
        except sqlite3.OperationalError as e:
            print(f"Database operational error updating last login: {e}")
            return False
        except Exception as e:
            print(f"Error updating last login: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    # Saved Courses Methods
    def save_course_for_user(self, user_id: int, course_id: str, notes: Optional[str] = None) -> bool:
        """Save a course to user's saved list"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO saved_courses (user_id, course_id, notes, saved_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, course_id, notes))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving course: {e}")
            return False
    
    def remove_saved_course(self, user_id: int, course_id: str) -> bool:
        """Remove a course from user's saved list"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM saved_courses WHERE user_id = ? AND course_id = ?', 
                          (user_id, course_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error removing saved course: {e}")
            return False
    
    def get_saved_courses(self, user_id: int) -> List[Dict]:
        """Get all saved courses for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, sc.saved_at, sc.notes
            FROM saved_courses sc
            JOIN courses c ON sc.course_id = c.id
            WHERE sc.user_id = ?
            ORDER BY sc.saved_at DESC
        ''', (user_id,))
        
        columns = [description[0] for description in cursor.description]
        saved_courses = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return saved_courses
    
    def is_course_saved(self, user_id: int, course_id: str) -> bool:
        """Check if a course is saved by user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM saved_courses WHERE user_id = ? AND course_id = ?', 
                      (user_id, course_id))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None