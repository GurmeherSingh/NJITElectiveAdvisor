#!/usr/bin/env python3
"""
NJIT Comprehensive Department System Setup
Updates database schema and creates department-specific templates
"""

import sqlite3
import pandas as pd
import os
import json
from typing import Dict, List

class NJITComprehensiveSystem:
    def __init__(self):
        self.db_path = "data/courses.db"
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directories"""
        os.makedirs("data/departments", exist_ok=True)
        os.makedirs("data/templates", exist_ok=True)
        
    def update_database_schema(self):
        """Update database schema to remove enrollment_count and add student ratings"""
        print("🔄 Updating database schema...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get existing course data
        cursor.execute("SELECT * FROM courses")
        existing_courses = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        print(f"   📊 Found {len(existing_courses)} existing courses")
        
        # Create new courses table without enrollment_count
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses_new (
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
                avg_rating REAL DEFAULT 0,
                total_ratings INTEGER DEFAULT 0
            )
        ''')
        
        # Copy existing data (excluding enrollment_count)
        for course in existing_courses:
            course_dict = dict(zip(columns, course))
            cursor.execute('''
                INSERT OR REPLACE INTO courses_new 
                (id, title, description, credits, prerequisites, department, 
                 level, difficulty_rating, career_relevance, topics, 
                 semester_offered, professor, avg_rating, total_ratings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                course_dict.get('id'),
                course_dict.get('title'),
                course_dict.get('description'),
                course_dict.get('credits'),
                course_dict.get('prerequisites'),
                course_dict.get('department'),
                course_dict.get('level'),
                course_dict.get('difficulty_rating'),
                course_dict.get('career_relevance'),
                course_dict.get('topics'),
                course_dict.get('semester_offered'),
                course_dict.get('professor'),
                course_dict.get('rating', 0),
                0  # total_ratings starts at 0
            ))
        
        # Drop old table and rename new one
        cursor.execute('DROP TABLE courses')
        cursor.execute('ALTER TABLE courses_new RENAME TO courses')
        
        # Create student ratings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_email TEXT,
                course_id TEXT,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                review TEXT,
                completed_semester TEXT,
                would_recommend BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses (id),
                UNIQUE(student_email, course_id)
            )
        ''')
        
        # Create comprehensive departments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                code TEXT UNIQUE,
                college TEXT,
                description TEXT,
                website TEXT,
                typical_electives TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("   ✅ Database schema updated successfully!")
        return len(existing_courses)
    
    def create_department_data(self):
        """Create comprehensive NJIT department data"""
        departments = {
            # Ying Wu College of Computing
            "Computer Science": {
                "code": "CS",
                "college": "Ying Wu College of Computing",
                "description": "Software engineering, AI/ML, cybersecurity, and systems",
                "website": "cs.njit.edu",
                "typical_electives": "CS480, CS485, CS490, CS435, CS656, CS643, CS634, CS675, CS670",
                "career_paths": ["Software Development", "AI/ML Engineering", "Cybersecurity", "Data Science", "Research"],
                "sample_courses": [
                    {
                        "id": "CS480", "title": "Introduction to Machine Learning",
                        "description": "Fundamentals of machine learning including supervised and unsupervised learning algorithms.",
                        "credits": 3, "prerequisites": "CS280, MATH333", "level": "Senior", "difficulty_rating": 4.3,
                        "career_relevance": "Data Science, AI Engineering, Machine Learning Engineer",
                        "topics": "Supervised Learning, Unsupervised Learning, Neural Networks, Data Mining",
                        "semester_offered": "Fall, Spring", "professor": "Dr. Chen"
                    },
                    {
                        "id": "CS485", "title": "Computer Security",
                        "description": "Introduction to computer security including cryptography and network security.",
                        "credits": 3, "prerequisites": "CS280, CS356", "level": "Senior", "difficulty_rating": 4.0,
                        "career_relevance": "Cybersecurity, Information Security, Security Engineering",
                        "topics": "Cryptography, Network Security, Vulnerability Assessment, Ethical Hacking",
                        "semester_offered": "Fall, Spring", "professor": "Dr. Smith"
                    },
                    {
                        "id": "CS490", "title": "Guided Design in Software Engineering",
                        "description": "Capstone course focusing on software engineering principles and team collaboration.",
                        "credits": 3, "prerequisites": "CS280, CS288", "level": "Senior", "difficulty_rating": 4.2,
                        "career_relevance": "Software Development, Project Management, Team Leadership",
                        "topics": "Software Engineering, Project Management, Team Collaboration, System Design",
                        "semester_offered": "Fall, Spring", "professor": "Various"
                    }
                ]
            },
            
            "Information Systems": {
                "code": "IS",
                "college": "Ying Wu College of Computing",
                "description": "Business-focused IT, data analytics, and information management",
                "website": "is.njit.edu",
                "typical_electives": "IS431, IS485, IS450, IS470",
                "career_paths": ["Business Analytics", "IT Management", "Systems Analysis", "Database Administration"],
                "sample_courses": [
                    {
                        "id": "IS431", "title": "Business Intelligence",
                        "description": "Data warehousing, OLAP, and business analytics for decision making.",
                        "credits": 3, "prerequisites": "IS117, IS219", "level": "Senior", "difficulty_rating": 3.5,
                        "career_relevance": "Business Analytics, Data Analysis, BI Developer",
                        "topics": "Data Warehousing, OLAP, Business Analytics, Reporting",
                        "semester_offered": "Fall, Spring", "professor": "Dr. Johnson"
                    },
                    {
                        "id": "IS485", "title": "Information Security Management",
                        "description": "Management of information security in organizations.",
                        "credits": 3, "prerequisites": "IS219, IS331", "level": "Senior", "difficulty_rating": 3.7,
                        "career_relevance": "IT Management, Security Management, Risk Assessment",
                        "topics": "Security Policies, Risk Management, Compliance, Governance",
                        "semester_offered": "Spring", "professor": "Dr. Brown"
                    }
                ]
            },
            
            "Data Science": {
                "code": "DS",
                "college": "Ying Wu College of Computing",
                "description": "Statistical analysis, machine learning, and big data analytics",
                "website": "ds.njit.edu",
                "typical_electives": "DS340, DS430, DS440, DS450",
                "career_paths": ["Data Scientist", "Business Analyst", "Data Engineer", "Research Scientist"],
                "sample_courses": [
                    {
                        "id": "DS340", "title": "Data Visualization",
                        "description": "Principles and techniques for effective data visualization.",
                        "credits": 3, "prerequisites": "DS280, MATH244", "level": "Junior", "difficulty_rating": 3.2,
                        "career_relevance": "Data Scientist, Business Analyst, Data Visualization Specialist",
                        "topics": "Visualization Design, Interactive Charts, Dashboard Creation",
                        "semester_offered": "Fall, Spring", "professor": "Dr. Lee"
                    },
                    {
                        "id": "DS430", "title": "Big Data Analytics",
                        "description": "Processing and analysis of large-scale datasets.",
                        "credits": 3, "prerequisites": "DS340, CS280", "level": "Senior", "difficulty_rating": 4.1,
                        "career_relevance": "Big Data Engineer, Data Scientist, Analytics Engineer",
                        "topics": "Hadoop, Spark, Distributed Computing, NoSQL",
                        "semester_offered": "Fall", "professor": "Dr. Wang"
                    }
                ]
            },
            
            # Newark College of Engineering
            "Civil Engineering": {
                "code": "CE",
                "college": "Newark College of Engineering",
                "description": "Infrastructure, construction, and environmental engineering",
                "website": "ce.njit.edu",
                "typical_electives": "CE465, CE463, CE455, CE475",
                "career_paths": ["Structural Engineering", "Transportation", "Environmental", "Construction Management"],
                "sample_courses": [
                    {
                        "id": "CE465", "title": "Green and Sustainable Civil Engineering",
                        "description": "Sustainable design principles in civil engineering projects.",
                        "credits": 3, "prerequisites": "CE332", "level": "Senior", "difficulty_rating": 3.8,
                        "career_relevance": "Environmental Engineering, Sustainability, Green Building",
                        "topics": "Green Building, Sustainability, Environmental Impact, LEED",
                        "semester_offered": "Spring", "professor": "Dr. Smith"
                    }
                ]
            },
            
            "Mechanical Engineering": {
                "code": "ME",
                "college": "Newark College of Engineering",
                "description": "Design, manufacturing, robotics, and thermal systems",
                "website": "me.njit.edu",
                "typical_electives": "ME456, ME460, ME470, ME480",
                "career_paths": ["Design Engineering", "Manufacturing", "Robotics", "Automotive", "Aerospace"],
                "sample_courses": [
                    {
                        "id": "ME456", "title": "Robotics and Automation",
                        "description": "Design and control of robotic systems and automated manufacturing.",
                        "credits": 3, "prerequisites": "ME345, ME380", "level": "Senior", "difficulty_rating": 4.0,
                        "career_relevance": "Robotics Engineer, Automation Engineer, Manufacturing",
                        "topics": "Robot Kinematics, Control Systems, Automation, Manufacturing",
                        "semester_offered": "Fall", "professor": "Dr. Kim"
                    }
                ]
            },
            
            "Electrical and Computer Engineering": {
                "code": "ECE",
                "college": "Newark College of Engineering",
                "description": "Electronics, communications, signal processing, and embedded systems",
                "website": "ece.njit.edu",
                "typical_electives": "ECE451, ECE465, ECE480, ECE490",
                "career_paths": ["Hardware Engineering", "Embedded Systems", "Signal Processing", "Telecommunications"],
                "sample_courses": [
                    {
                        "id": "ECE451", "title": "Digital Signal Processing",
                        "description": "Theory and applications of digital signal processing.",
                        "credits": 3, "prerequisites": "ECE345, MATH222", "level": "Senior", "difficulty_rating": 4.3,
                        "career_relevance": "Signal Processing Engineer, Communications, Audio/Video Processing",
                        "topics": "FFT, Digital Filters, Signal Analysis, DSP Applications",
                        "semester_offered": "Spring", "professor": "Dr. Martinez"
                    }
                ]
            },
            
            "Chemical Engineering": {
                "code": "CHE",
                "college": "Newark College of Engineering",
                "description": "Process engineering, biotechnology, and materials",
                "website": "che.njit.edu",
                "typical_electives": "CHE450, CHE460, CHE470, CHE480",
                "career_paths": ["Process Engineering", "Biotechnology", "Environmental", "Pharmaceuticals"],
                "sample_courses": [
                    {
                        "id": "CHE450", "title": "Bioprocess Engineering",
                        "description": "Application of engineering principles to biological processes.",
                        "credits": 3, "prerequisites": "CHE349, CHE370", "level": "Senior", "difficulty_rating": 4.1,
                        "career_relevance": "Biotechnology, Pharmaceuticals, Bioprocess Engineering",
                        "topics": "Bioprocessing, Fermentation, Bioreactors, Process Design",
                        "semester_offered": "Fall", "professor": "Dr. Wilson"
                    }
                ]
            },
            
            "Biomedical Engineering": {
                "code": "BME",
                "college": "Newark College of Engineering",
                "description": "Medical devices, biomaterials, and healthcare technology",
                "website": "bme.njit.edu",
                "typical_electives": "BME450, BME460, BME470, BME480",
                "career_paths": ["Medical Devices", "Biomaterials", "Biotech", "Healthcare Technology"],
                "sample_courses": [
                    {
                        "id": "BME450", "title": "Medical Device Design",
                        "description": "Design and development of medical devices and instruments.",
                        "credits": 3, "prerequisites": "BME345, BME360", "level": "Senior", "difficulty_rating": 3.9,
                        "career_relevance": "Medical Device Engineering, Product Development, Healthcare Technology",
                        "topics": "Device Design, FDA Regulations, Biocompatibility, Testing",
                        "semester_offered": "Fall", "professor": "Dr. Garcia"
                    }
                ]
            },
            
            # Martin Tuchman School of Management
            "Management": {
                "code": "MGMT",
                "college": "Martin Tuchman School of Management",
                "description": "Business strategy, entrepreneurship, and technology management",
                "website": "management.njit.edu",
                "typical_electives": "MGMT451, MGMT460, MGMT470, ENTR420",
                "career_paths": ["Management", "Entrepreneurship", "Product Manager", "Technology Manager"],
                "sample_courses": [
                    {
                        "id": "MGMT451", "title": "Technology Entrepreneurship",
                        "description": "Starting and managing technology-based ventures.",
                        "credits": 3, "prerequisites": "MGMT301", "level": "Senior", "difficulty_rating": 3.0,
                        "career_relevance": "Entrepreneur, Product Manager, Technology Manager, Startup Founder",
                        "topics": "Startup Management, Product Development, Venture Capital, Innovation",
                        "semester_offered": "Fall, Spring", "professor": "Dr. Garcia"
                    },
                    {
                        "id": "ENTR420", "title": "Digital Innovation and Strategy",
                        "description": "Strategic approaches to digital transformation and innovation.",
                        "credits": 3, "prerequisites": "MGMT390", "level": "Senior", "difficulty_rating": 3.3,
                        "career_relevance": "Digital Strategy, Innovation Management, Product Strategy",
                        "topics": "Digital Transformation, Innovation Strategy, Technology Adoption",
                        "semester_offered": "Spring", "professor": "Dr. Thompson"
                    }
                ]
            },
            
            # Jordan Hu College of Science and Liberal Arts
            "Biology": {
                "code": "BIOL",
                "college": "Jordan Hu College of Science and Liberal Arts",
                "description": "Life sciences, biotechnology, and environmental biology",
                "website": "biology.njit.edu",
                "typical_electives": "BIOL456, BIOL460, BIOL470, BIOL480",
                "career_paths": ["Biotechnology", "Research", "Environmental Science", "Healthcare"],
                "sample_courses": [
                    {
                        "id": "BIOL456", "title": "Biotechnology Applications",
                        "description": "Applications of biotechnology in industry and medicine.",
                        "credits": 3, "prerequisites": "BIOL352", "level": "Senior", "difficulty_rating": 4.1,
                        "career_relevance": "Biotechnology, Research, Pharmaceuticals, Healthcare",
                        "topics": "Genetic Engineering, Bioprocessing, Medical Applications",
                        "semester_offered": "Fall", "professor": "Dr. Lee"
                    }
                ]
            },
            
            "Chemistry": {
                "code": "CHEM",
                "college": "Jordan Hu College of Science and Liberal Arts",
                "description": "Chemical research, materials science, and analytical chemistry",
                "website": "chemistry.njit.edu",
                "typical_electives": "CHEM450, CHEM460, CHEM470, CHEM480",
                "career_paths": ["Research", "Materials Science", "Pharmaceuticals", "Environmental"],
                "sample_courses": [
                    {
                        "id": "CHEM450", "title": "Advanced Materials Chemistry",
                        "description": "Synthesis and characterization of advanced materials.",
                        "credits": 3, "prerequisites": "CHEM335, CHEM474", "level": "Senior", "difficulty_rating": 4.2,
                        "career_relevance": "Materials Science, Research, Nanotechnology",
                        "topics": "Nanomaterials, Polymers, Characterization Techniques",
                        "semester_offered": "Spring", "professor": "Dr. Chen"
                    }
                ]
            },
            
            "Mathematics": {
                "code": "MATH",
                "college": "Jordan Hu College of Science and Liberal Arts",
                "description": "Applied mathematics, statistics, and computational methods",
                "website": "math.njit.edu",
                "typical_electives": "MATH450, MATH460, MATH470, MATH480",
                "career_paths": ["Applied Mathematics", "Statistics", "Financial Mathematics", "Research"],
                "sample_courses": [
                    {
                        "id": "MATH450", "title": "Mathematical Modeling",
                        "description": "Mathematical techniques for modeling real-world problems.",
                        "credits": 3, "prerequisites": "MATH333, MATH337", "level": "Senior", "difficulty_rating": 4.0,
                        "career_relevance": "Applied Mathematics, Research, Data Science, Engineering",
                        "topics": "Differential Equations, Optimization, Simulation, Modeling",
                        "semester_offered": "Fall", "professor": "Dr. Rodriguez"
                    }
                ]
            },
            
            # Hillier College of Architecture and Design
            "Architecture": {
                "code": "ARCH",
                "college": "Hillier College of Architecture and Design",
                "description": "Architectural design, urban planning, and sustainable design",
                "website": "architecture.njit.edu",
                "typical_electives": "ARCH415, ARCH425, ARCH435, ARCH445",
                "career_paths": ["Architectural Design", "Urban Planning", "Sustainable Design", "Construction"],
                "sample_courses": [
                    {
                        "id": "ARCH415", "title": "Sustainable Design",
                        "description": "Sustainable and energy-efficient architectural design principles.",
                        "credits": 3, "prerequisites": "ARCH301", "level": "Senior", "difficulty_rating": 3.7,
                        "career_relevance": "Sustainable Architecture, Green Design, Environmental Design",
                        "topics": "LEED, Green Building, Energy Efficiency, Sustainable Materials",
                        "semester_offered": "Spring", "professor": "Dr. Brown"
                    }
                ]
            },
            
            "Digital Design": {
                "code": "ARTD",
                "college": "Hillier College of Architecture and Design",
                "description": "UI/UX design, digital media, and interactive design",
                "website": "digitaldesign.njit.edu",
                "typical_electives": "ARTD340, ARTD350, ARTD360, ARTD370",
                "career_paths": ["UI/UX Design", "Graphic Design", "Digital Media", "Game Design"],
                "sample_courses": [
                    {
                        "id": "ARTD340", "title": "User Experience Design",
                        "description": "Design principles for user-centered digital products.",
                        "credits": 3, "prerequisites": "ARTD201", "level": "Junior", "difficulty_rating": 3.2,
                        "career_relevance": "UI/UX Design, Product Design, Human-Computer Interaction",
                        "topics": "User Research, Prototyping, Interface Design, Usability Testing",
                        "semester_offered": "Fall, Spring", "professor": "Dr. Wilson"
                    }
                ]
            }
        }
        
        return departments
    
    def save_department_data(self, departments):
        """Save department data to database"""
        print("💾 Saving department data...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for dept_name, dept_info in departments.items():
            cursor.execute('''
                INSERT OR REPLACE INTO departments 
                (name, code, college, description, website, typical_electives)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                dept_name,
                dept_info["code"],
                dept_info["college"],
                dept_info["description"],
                dept_info["website"],
                dept_info["typical_electives"]
            ))
        
        conn.commit()
        conn.close()
        print(f"   ✅ Saved {len(departments)} departments")
    
    def create_department_templates(self, departments):
        """Create CSV templates for each department"""
        print("📝 Creating department templates...")
        
        templates_created = []
        
        for dept_name, dept_info in departments.items():
            # Create template with sample courses
            sample_courses = dept_info.get("sample_courses", [])
            
            # Add department to each course
            for course in sample_courses:
                course["department"] = dept_name
            
            # Create DataFrame
            df = pd.DataFrame(sample_courses)
            
            # Save as CSV
            filename = f"data/departments/{dept_info['code']}_electives.csv"
            df.to_csv(filename, index=False)
            templates_created.append(filename)
            
            print(f"   📄 Created: {filename} ({len(sample_courses)} sample courses)")
        
        return templates_created
    
    def create_comprehensive_template(self, departments):
        """Create one comprehensive template with all departments"""
        print("📋 Creating comprehensive template...")
        
        all_courses = []
        for dept_name, dept_info in departments.items():
            dept_courses = dept_info.get("sample_courses", [])
            for course in dept_courses:
                course["department"] = dept_name
            all_courses.extend(dept_courses)
        
        df = pd.DataFrame(all_courses)
        filename = "data/comprehensive_njit_electives.csv"
        df.to_csv(filename, index=False)
        
        print(f"   ✅ Created: {filename} ({len(all_courses)} courses across {len(departments)} departments)")
        return filename
    
    def create_collection_guide(self, departments):
        """Create comprehensive data collection guide"""
        guide = {
            "title": "NJIT Comprehensive Elective Data Collection Guide",
            "version": "2.0",
            "overview": "Complete guide for collecting elective course data across ALL NJIT departments",
            "instructions": [
                "1. Choose a department from the templates below",
                "2. Research courses using NJIT catalog (catalog.njit.edu)",
                "3. Fill in the CSV template with real course data",
                "4. Import using the data manager",
                "5. Enable student ratings for real user feedback"
            ],
            "data_sources": [
                "NJIT Course Catalog: catalog.njit.edu",
                "Department websites",
                "Course schedules and syllabi",
                "Academic advisors",
                "Student reviews and feedback"
            ],
            "departments": {},
            "rating_system": {
                "description": "Students can rate courses they've completed",
                "rating_scale": "1-5 stars",
                "fields": ["Overall rating", "Difficulty", "Usefulness", "Would recommend", "Written review"],
                "authentication": "Student email required to prevent duplicate ratings"
            },
            "required_fields": {
                "id": "Course code (e.g., CS480, ME456)",
                "title": "Course title",
                "description": "2-3 sentence description",
                "credits": "Number of credits (typically 3)",
                "prerequisites": "Required courses or 'None'",
                "department": "Department name",
                "level": "Undergraduate/Graduate/Senior/Junior",
                "difficulty_rating": "Estimated difficulty 1-5",
                "career_relevance": "Career paths this supports",
                "topics": "Key topics covered",
                "semester_offered": "Fall/Spring/Summer",
                "professor": "Typical instructor"
            }
        }
        
        # Add department-specific info
        for dept_name, dept_info in departments.items():
            guide["departments"][dept_name] = {
                "code": dept_info["code"],
                "college": dept_info["college"],
                "focus_areas": dept_info["career_paths"],
                "template_file": f"data/departments/{dept_info['code']}_electives.csv",
                "website": dept_info["website"],
                "typical_electives": dept_info["typical_electives"],
                "sample_count": len(dept_info.get("sample_courses", []))
            }
        
        # Save guide
        filename = "data/comprehensive_collection_guide.json"
        with open(filename, 'w') as f:
            json.dump(guide, f, indent=2)
        
        print(f"   📖 Created collection guide: {filename}")
        return filename
    
    def run_setup(self):
        """Run complete setup process"""
        print("🎓 NJIT Comprehensive Department System Setup")
        print("=" * 60)
        
        # Step 1: Update database
        existing_count = self.update_database_schema()
        
        # Step 2: Create department data
        departments = self.create_department_data()
        
        # Step 3: Save to database
        self.save_department_data(departments)
        
        # Step 4: Create templates
        templates = self.create_department_templates(departments)
        
        # Step 5: Create comprehensive template
        comprehensive_file = self.create_comprehensive_template(departments)
        
        # Step 6: Create guide
        guide_file = self.create_collection_guide(departments)
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 Setup Complete!")
        print("=" * 60)
        print(f"✅ Updated database (preserved {existing_count} existing courses)")
        print(f"✅ Added {len(departments)} NJIT departments")
        print(f"✅ Created {len(templates)} department templates")
        print(f"✅ Created comprehensive template: {comprehensive_file}")
        print(f"✅ Created collection guide: {guide_file}")
        print("✅ Added student rating system")
        
        print("\n🎯 What you have now:")
        print("• Database without enrollment_count")
        print("• Student rating system ready")
        print("• Templates for ALL NJIT departments")
        print("• Comprehensive data collection guide")
        
        print("\n📋 Next Steps:")
        print("1. Fill in department templates with real NJIT courses")
        print("2. Import completed templates using setup_data.py")
        print("3. Test the student rating system")
        print("4. Deploy for NJIT students to use!")
        
        return {
            "departments": len(departments),
            "templates": templates,
            "comprehensive_file": comprehensive_file,
            "guide_file": guide_file
        }

if __name__ == "__main__":
    system = NJITComprehensiveSystem()
    results = system.run_setup()