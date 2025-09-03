# 🎓 NJIT Smart Elective Advisor

An AI-powered course recommendation system designed specifically for NJIT students to make informed decisions about their elective courses. The system analyzes student interests, career goals, and academic background to provide personalized course recommendations.

## 🚀 Features

- **Personalized Recommendations**: AI-driven course suggestions based on interests and career goals
- **Smart Matching**: Advanced algorithms that consider difficulty preferences, prerequisites, and course ratings
- **Interactive Web Interface**: Modern, responsive UI for easy course discovery
- **Detailed Analysis**: Score breakdowns showing why each course was recommended
- **Comprehensive Database**: Extensive NJIT course catalog with detailed metadata

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Machine Learning**: Scikit-learn, NLTK, TF-IDF Vectorization
- **Database**: SQLite
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Data Processing**: Pandas, NumPy

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd NJITElectiveAdvisor
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**:
   ```bash
   python setup_data.py
   # Choose option 1 to load sample data
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the web interface**:
   Open your browser and go to `http://localhost:5000`

## 🎯 How It Works

### 1. Input Collection
Students provide:
- **Interests**: Areas like AI/ML, Web Development, Cybersecurity, etc.
- **Career Goals**: Target roles like Software Developer, Data Scientist, etc.
- **Difficulty Preference**: Easy, Medium, or Challenging courses
- **Completed Courses**: Prerequisites already satisfied

### 2. AI Recommendation Engine
The system uses multiple algorithms to score courses:

- **Interest Matching** (25%): TF-IDF cosine similarity between student interests and course content
- **Career Alignment** (30%): Keyword matching with career-relevant topics
- **Difficulty Fit** (15%): Alignment between preferred and actual course difficulty
- **Prerequisites** (20%): Verification of prerequisite completion
- **Popularity Score** (10%): Course ratings and enrollment data

### 3. Personalized Results
Each recommendation includes:
- Overall match percentage
- Detailed score breakdown
- Explanation of why the course was recommended
- Course metadata (credits, prerequisites, ratings)

## 📊 Sample Courses Included

The system comes with real NJIT CS courses:
- **CS490**: Guided Design in Software Engineering
- **CS480**: Introduction to Machine Learning
- **CS485**: Computer Security
- **CS435**: Advanced Data Structures and Algorithms
- **CS656**: Internet and Higher Layer Protocols
- **CS643**: Web Mining
- **CS634**: Data Mining
- **CS631**: Data Management System Design
- **CS675**: Introduction to Computer Graphics
- **CS670**: Artificial Intelligence

## 🔧 API Endpoints

### Get All Courses
```
GET /api/courses
```

### Get Recommendations
```
POST /api/recommend
Content-Type: application/json

{
  "interests": ["artificial intelligence", "web development"],
  "career_goals": "software_development",
  "difficulty_preference": "medium",
  "completed_courses": ["CS280", "CS288"]
}
```

### Get Course Details
```
GET /api/course/<course_id>
```

### Submit Feedback
```
POST /api/feedback
Content-Type: application/json

{
  "student_id": "student123",
  "recommended_courses": ["CS480", "CS485"],
  "selected_courses": ["CS480"],
  "rating": 5,
  "comments": "Great recommendations!"
}
```

## 📈 Extending the System

### Adding More Courses

1. **Using CSV Import**:
   ```bash
   python setup_data.py
   # Choose option 2 to create CSV template
   # Edit the CSV file with new courses
   # Choose option 3 to import
   ```

2. **Manual Database Entry**:
   Use the DataManager class to add courses programmatically.

3. **Web Scraping** (Future):
   Implement automated scraping of NJIT's course catalog.

### Improving Recommendations

The recommendation algorithm can be enhanced by:
- Adding more sophisticated NLP techniques
- Incorporating student feedback for model improvement
- Adding collaborative filtering based on similar students
- Including time-series analysis for course availability

## 🎨 User Interface Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive Forms**: Easy-to-use checkboxes and dropdowns
- **Real-time Results**: Instant recommendations without page refresh
- **Score Visualization**: Clear breakdown of recommendation reasoning
- **Modern Styling**: Bootstrap-based UI with custom styling

## 🔍 Testing the System

Try these sample inputs:

**AI/ML Enthusiast**:
- Interests: AI/ML, Data Science
- Career Goal: Data Scientist
- Difficulty: Medium
- Completed: CS280, CS341

**Security Professional**:
- Interests: Cybersecurity, Networking
- Career Goal: Cybersecurity Specialist
- Difficulty: Challenging
- Completed: CS280, CS356

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add new courses or improve algorithms
4. Test your changes
5. Submit a pull request

## 📝 Future Enhancements

- [ ] Integration with NJIT's official course catalog
- [ ] Student login and preference saving
- [ ] Course prerequisite visualization
- [ ] Semester planning tools
- [ ] Professor ratings integration
- [ ] Course difficulty prediction based on student GPA
- [ ] Mobile application
- [ ] Integration with degree audit systems

## 📄 License

This project is created for educational purposes at NJIT.

## 👥 Contact

For questions or suggestions about the NJIT Smart Elective Advisor, please reach out to the development team.

---

**Made with ❤️ for NJIT students**