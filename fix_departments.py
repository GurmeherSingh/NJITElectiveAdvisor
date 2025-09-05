#!/usr/bin/env python3
"""
Quick fix for departments table schema issue
"""

import sqlite3
import os

def fix_departments_table(db_path="data/courses.db"):
    """Fix the departments table schema and populate it"""
    
    print("Fixing departments table...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop the existing departments table and recreate it properly
        print("Dropping existing departments table...")
        cursor.execute("DROP TABLE IF EXISTS departments")
        
        # Create departments table with correct schema
        print("Creating departments table with correct schema...")
        cursor.execute('''
            CREATE TABLE departments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                full_name TEXT,
                description TEXT,
                website TEXT,
                contact_email TEXT,
                total_courses INTEGER DEFAULT 0
            )
        ''')
        
        # Populate with NJIT departments
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
                INSERT INTO departments (id, name, full_name)
                VALUES (?, ?, ?)
            ''', (dept_id, name, full_name))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Successfully fixed departments table with {len(departments)} departments")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix departments table: {e}")
        return False

if __name__ == "__main__":
    success = fix_departments_table()
    if success:
        print("🎉 Departments table fixed successfully!")
    else:
        print("💥 Failed to fix departments table")
        exit(1)

