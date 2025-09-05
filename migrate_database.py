#!/usr/bin/env python3
"""
Database migration script to fix schema issues for NJIT Elective Advisor
This script adds missing tables and columns that are causing the server errors.
"""

import sqlite3
import os
import sys

def migrate_database(db_path="data/courses.db"):
    """Migrate the database to add missing tables and columns"""
    
    print(f"Starting database migration for: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database file does not exist: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Add missing columns to courses table
        print("Adding missing columns to courses table...")
        try:
            cursor.execute("ALTER TABLE courses ADD COLUMN avg_rating REAL DEFAULT 0.0")
            print("Added avg_rating column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("avg_rating column already exists")
            else:
                print(f"Error adding avg_rating: {e}")
        
        try:
            cursor.execute("ALTER TABLE courses ADD COLUMN total_ratings INTEGER DEFAULT 0")
            print("Added total_ratings column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("total_ratings column already exists")
            else:
                print(f"Error adding total_ratings: {e}")
        
        # 2. Create student_ratings table
        print("Creating student_ratings table...")
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
        print("student_ratings table created/verified")
        
        # 3. Create departments table
        print("Creating departments table...")
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
        print("departments table created/verified")
        
        # 4. Populate departments table
        print("Populating departments table...")
        departments = [
            ("CS", "Computer Science", "Computer Science Department"),
            ("ECE", "Electrical & Computer Engineering", "Electrical & Computer Engineering Department"),
            ("ME", "Mechanical Engineering", "Mechanical Engineering Department"),
            ("CE", "Civil Engineering", "Civil Engineering Department"),
            ("CHE", "Chemical Engineering", "Chemical Engineering Department"),
            ("BME", "Biomedical Engineering", "Biomedical Engineering Department"),
            ("MATH", "Mathematics", "Mathematical Sciences Department"),
            ("PHYS", "Physics", "Physics Department"),
            ("CHEM", "Chemistry", "Chemistry & Environmental Science Department"),
            ("BIOL", "Biology", "Biological Sciences Department"),
            ("MGMT", "Management", "School of Management"),
            ("FIN", "Finance", "Finance Department"),
            ("ACCT", "Accounting", "Accounting Department"),
            ("MIS", "Management Information Systems", "Management Information Systems Department"),
            ("IS", "Information Systems", "Information Systems Department"),
            ("IT", "Information Technology", "Information Technology Department"),
            ("DS", "Data Science", "Data Science Department"),
            ("ARCH", "Architecture", "School of Architecture"),
            ("ARTD", "Art & Design", "Art & Design Department"),
            ("ENG", "English", "Humanities Department"),
            ("SLA", "Science, Liberal Arts", "Science, Liberal Arts Department")
        ]
        
        for dept_id, name, full_name in departments:
            cursor.execute('''
                INSERT OR REPLACE INTO departments (id, name, full_name)
                VALUES (?, ?, ?)
            ''', (dept_id, name, full_name))
        
        print(f"Populated {len(departments)} departments")
        
        # 5. Update existing courses that might have NULL avg_rating/total_ratings
        print("Updating existing courses with default rating values...")
        cursor.execute('''
            UPDATE courses 
            SET avg_rating = COALESCE(avg_rating, 0.0),
                total_ratings = COALESCE(total_ratings, 0)
            WHERE avg_rating IS NULL OR total_ratings IS NULL
        ''')
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        print("Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Database migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def main():
    """Main function to run the migration"""
    # Default database path
    db_path = "data/courses.db"
    
    # Allow custom path as command line argument
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    print("NJIT Elective Advisor - Database Migration Script")
    print("=" * 50)
    
    success = migrate_database(db_path)
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("The database has been updated with the required schema changes.")
        print("You can now restart your application server.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
