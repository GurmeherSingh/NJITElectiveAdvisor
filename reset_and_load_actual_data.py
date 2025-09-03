#!/usr/bin/env python3
"""
NJIT Elective Advisor - Reset Database and Load Actual Course Data

This script:
1. Clears all existing sample course data from the database
2. Loads all actual NJIT course data from the CSV files in data/departments/
3. Provides statistics on the loaded data
"""

import os
import sqlite3
import pandas as pd
import glob
from src.data_manager import DataManager

def clear_existing_courses(db_path="data/courses.db"):
    """Clear all existing courses from the database"""
    print("🗑️  Clearing existing course data...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Delete all courses
    cursor.execute("DELETE FROM courses")
    
    # Reset auto-increment if needed
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='courses'")
    
    conn.commit()
    conn.close()
    print("✅ Existing course data cleared")

def load_csv_files(db_path="data/courses.db"):
    """Load all CSV files from data/departments/ into the database"""
    csv_files = glob.glob("data/departments/*.csv")
    
    if not csv_files:
        print("❌ No CSV files found in data/departments/")
        return 0
    
    print(f"📁 Found {len(csv_files)} CSV files to import...")
    
    conn = sqlite3.connect(db_path)
    total_courses = 0
    
    for csv_file in sorted(csv_files):
        print(f"   Loading {os.path.basename(csv_file)}...")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Skip empty files
            if df.empty:
                print(f"   ⚠️  Skipping empty file: {csv_file}")
                continue
            
            # Add default values for missing database columns
            if 'avg_rating' not in df.columns:
                df['avg_rating'] = 0.0
            
            if 'total_ratings' not in df.columns:
                df['total_ratings'] = 0
            
            # Load into database
            df.to_sql('courses', conn, if_exists='append', index=False)
            total_courses += len(df)
            print(f"   ✅ Loaded {len(df)} courses from {os.path.basename(csv_file)}")
            
        except Exception as e:
            print(f"   ❌ Error loading {csv_file}: {e}")
    
    conn.close()
    return total_courses

def verify_database_structure(db_path="data/courses.db"):
    """Verify the database has the correct structure"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("PRAGMA table_info(courses)")
    columns = cursor.fetchall()
    
    print("\n📊 Database Structure:")
    for col in columns:
        print(f"   {col[1]} ({col[2]})")
    
    conn.close()

def show_import_statistics(db_path="data/courses.db"):
    """Show statistics about the imported data"""
    data_manager = DataManager(db_path)
    stats = data_manager.get_course_statistics()
    
    print("\n📈 Import Statistics:")
    print(f"   Total Courses: {stats['total_courses']}")
    print(f"   Average Difficulty: {stats['average_difficulty']}/5.0")
    print(f"   Average Rating: {stats['average_rating']}/5.0")
    
    print("\n🏛️  Courses by Department:")
    for dept, count in sorted(stats['departments'].items()):
        print(f"   {dept}: {count} courses")

def main():
    print("=== NJIT Elective Advisor - Database Reset & Data Import ===\n")
    
    # Check if database exists
    db_path = "data/courses.db"
    if not os.path.exists(db_path):
        print("Creating new database...")
        data_manager = DataManager(db_path)
    
    # Clear existing data
    clear_existing_courses(db_path)
    
    # Verify database structure
    verify_database_structure(db_path)
    
    # Load actual course data
    total_imported = load_csv_files(db_path)
    
    if total_imported > 0:
        print(f"\n🎉 Successfully imported {total_imported} courses!")
        
        # Show statistics
        show_import_statistics(db_path)
        
        print("\n🚀 Next Steps:")
        print("   1. Run the application: python app.py")
        print("   2. Access the web interface: http://localhost:5000")
        print("   3. Test the recommendation system with actual NJIT course data!")
        
    else:
        print("\n❌ No courses were imported. Please check your CSV files.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nImport interrupted.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your setup and try again.")