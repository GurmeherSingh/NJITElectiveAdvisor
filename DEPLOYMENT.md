# 🚀 NJIT Elective Advisor - Production Deployment Guide

## 📋 Overview

The NJIT Elective Advisor is now production-ready with full user authentication, course saving functionality, and security features. This guide covers deployment and operation.

## ✨ Features Implemented

### 🔐 Authentication System
- **User Registration**: Secure account creation with email validation
- **User Login**: Session-based authentication with secure password hashing
- **Password Security**: PBKDF2 hashing with salt, strong password requirements
- **Session Management**: Secure session handling with configurable timeouts

### 💾 User Features
- **Save Courses**: Users can save recommended courses to their personal list
- **Saved Courses Page**: Dedicated page to manage saved courses
- **User Dashboard**: Navigation with personalized welcome messages
- **Course Management**: Add/remove courses from saved list

### 🛡️ Security Features
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, XSS Protection
- **Content Security Policy**: Configurable CSP for production environments
- **Session Security**: HTTPOnly, Secure, and SameSite cookie attributes
- **Input Validation**: Email validation, password strength requirements
- **SQL Injection Protection**: Parameterized queries throughout

### 🗄️ Database Schema
- **Users Table**: Stores user accounts with encrypted passwords
- **Saved Courses Table**: Links users to their saved courses with timestamps
- **Foreign Key Constraints**: Maintains data integrity
- **Indexed Queries**: Optimized for performance

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
# At minimum, set a strong SECRET_KEY
```

### 3. Initialize Database
```bash
# Populate with course data (if not already done)
python reset_and_load_actual_data.py
```

### 4. Start Application
```bash
# Development mode
python run.py

# Production mode
FLASK_ENV=production python run.py
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Required for production
SECRET_KEY=your-super-secret-key-here-256-bits-recommended
FLASK_ENV=production
FLASK_DEBUG=False

# Security settings
SESSION_COOKIE_SECURE=True  # Requires HTTPS
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Server configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Database
DATABASE_URL=sqlite:///data/courses.db
```

### Production Security Checklist

- [ ] Set strong `SECRET_KEY` (use `secrets.token_hex(32)`)
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Enable `SESSION_COOKIE_SECURE=True` (requires HTTPS)
- [ ] Configure reverse proxy (nginx/Apache) for HTTPS
- [ ] Set up firewall rules
- [ ] Configure backup strategy for database

## 🗄️ Database Management

### Tables Created Automatically
- `users` - User accounts and profiles
- `saved_courses` - User's saved course lists
- `courses` - Course catalog (populated separately)
- `student_preferences` - Recommendation preferences
- `feedback` - User feedback and ratings

### Database Operations
```python
# Create a user programmatically
from src.data_manager import DataManager
from src.auth import AuthManager

dm = DataManager()
auth = AuthManager(dm)

success, message, user_id = auth.register_user(
    email="admin@njit.edu",
    password="SecurePassword123",
    first_name="Admin",
    last_name="User"
)
```

## 🌐 Deployment Options

### 1. Local Development Server
```bash
python run.py
# Access at http://localhost:5000
```

### 2. Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 3. Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

### 4. Cloud Deployment (Heroku/Railway/DigitalOcean)
- Set environment variables in platform settings
- Use PostgreSQL for production database (optional)
- Configure HTTPS and domain settings

## 🧪 Testing the System

### Authentication Flow Test
1. Visit `/register` - Create a new account
2. Visit `/login` - Sign in with credentials
3. Homepage should show "Welcome, [Name]!" in navbar
4. Click "Saved Courses" - Should show empty state initially

### Course Saving Test
1. Get course recommendations on homepage
2. Click "Save Course" on any recommendation
3. Should see success message and button changes to "Saved!"
4. Visit "Saved Courses" page - Should show saved course
5. Click "Remove" to test removal functionality

### Security Test
1. Try accessing `/saved-courses` without login - Should redirect to login
2. Try accessing `/api/saved-courses` without login - Should return 401
3. Check browser developer tools for security headers

## 🔍 Monitoring and Logs

### Application Logs
```python
# Enable logging in production
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Key Metrics to Monitor
- User registration rate
- Login success/failure rates
- Course save/remove operations
- Page load times
- Error rates

## 🛠️ Maintenance

### Regular Tasks
- **Database Backup**: Regular SQLite database file backups
- **Log Rotation**: Manage application log files
- **Security Updates**: Keep dependencies updated
- **Course Data Updates**: Refresh course catalog as needed

### Updating Course Data
```bash
# Update course database
python reset_and_load_actual_data.py
```

## 🆘 Troubleshooting

### Common Issues

**Users can't register**
- Check email validation
- Verify database permissions
- Check password requirements

**Authentication not working**
- Verify `SECRET_KEY` is set
- Check session cookie settings
- Ensure database users table exists

**Courses not loading**
- Run `python reset_and_load_actual_data.py`
- Check database file permissions
- Verify course data import

**Production security warnings**
- Enable HTTPS and set `SESSION_COOKIE_SECURE=True`
- Configure proper CSP headers
- Set up reverse proxy (nginx)

## 📞 Support

For issues or questions:
1. Check this deployment guide
2. Review application logs
3. Test with fresh database
4. Verify environment configuration

## 🎉 Success!

Your NJIT Elective Advisor is now production-ready with:
- ✅ User authentication and registration
- ✅ Course saving and management
- ✅ Security best practices
- ✅ Production configuration
- ✅ Scalable architecture

Users can now:
- Create accounts and sign in securely
- Get personalized course recommendations
- Save courses for future reference
- Manage their saved course lists

**Ready for real student use!** 🎓