#!/usr/bin/env python3
"""
NJIT Elective Advisor - Data Setup Script

This script helps you set up the knowledge base for the NJIT Elective Advisor.
You have several options for populating the course database:

1. Use sample data (quick start)
2. Import from CSV file
3. Manual data entry
4. Web scraping (future enhancement)
"""

import os
import sys
from src.data_manager import DataManager
from src.data_collector import NJITDataCollector

def main():
    print("=== NJIT Elective Advisor - Data Setup ===\n")
    
    # Initialize components
    data_manager = DataManager()
    collector = NJITDataCollector()
    
    print("Choose your data setup method:")
    print("1. Load sample data (Quick start - recommended)")
    print("2. Create CSV template for manual data entry")
    print("3. Import from existing CSV file")
    print("4. View current database statistics")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        print("\nLoading sample NJIT course data...")
        data_manager.load_sample_data()
        print("✅ Sample data loaded successfully!")
        print("\nNext steps:")
        print("- Review the sample data in data/courses.db")
        print("- Add more courses using option 2 or 3")
        print("- Run the application: python app.py")
        
    elif choice == "2":
        print("\nCreating CSV template...")
        csv_file = collector.create_sample_csv()
        template_file = collector.create_data_template()
        print(f"✅ Files created:")
        print(f"- Sample CSV: {csv_file}")
        print(f"- Template: {template_file}")
        print("\nNext steps:")
        print("- Edit the CSV file to add more NJIT courses")
        print("- Use option 3 to import your updated CSV")
        
    elif choice == "3":
        csv_path = input("Enter path to your CSV file: ").strip()
        if os.path.exists(csv_path):
            print(f"Importing courses from {csv_path}...")
            data_manager.import_courses_from_csv(csv_path)
            print("✅ Import completed!")
        else:
            print("❌ File not found. Please check the path.")
            
    elif choice == "4":
        print("\nDatabase Statistics:")
        stats = data_manager.get_course_statistics()
        print(f"Total Courses: {stats['total_courses']}")
        print(f"Average Difficulty: {stats['average_difficulty']}/5.0")
        print(f"Average Rating: {stats['average_rating']}/5.0")
        print("\nCourses by Department:")
        for dept, count in stats['departments'].items():
            print(f"  {dept}: {count} courses")
            
    elif choice == "5":
        print("Goodbye!")
        sys.exit(0)
        
    else:
        print("Invalid choice. Please try again.")
        main()

def show_next_steps():
    print("\n" + "="*50)
    print("🎓 NJIT Elective Advisor Setup Complete!")
    print("="*50)
    print("\nWhat you can do now:")
    print("1. Run the application:")
    print("   python app.py")
    print("\n2. Access the web interface:")
    print("   http://localhost:5000")
    print("\n3. Add more course data:")
    print("   python setup_data.py")
    print("\n4. Test the API endpoints:")
    print("   curl http://localhost:5000/api/courses")
    print("\n5. Customize the recommendation algorithm:")
    print("   Edit src/recommendation_engine.py")

if __name__ == "__main__":
    try:
        main()
        show_next_steps()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted. You can run this script again anytime.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your setup and try again.")