#!/bin/bash

# NJIT Elective Advisor - Production Server Fix Script
# This script fixes the database schema issues causing internal server errors

echo "🔧 NJIT Elective Advisor - Production Server Fix"
echo "================================================"

# Check if running as correct user
if [ "$USER" != "njit-advisor" ]; then
    echo "⚠️  Warning: This script should be run as the 'njit-advisor' user"
    echo "   Current user: $USER"
    echo "   Switch with: sudo su - njit-advisor"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Set working directory
APP_DIR="/opt/njit-advisor/app"
cd "$APP_DIR" || {
    echo "❌ Could not change to application directory: $APP_DIR"
    exit 1
}

echo "📍 Working directory: $(pwd)"

# Check if virtual environment exists
if [ ! -d "/opt/njit-advisor/venv" ]; then
    echo "❌ Virtual environment not found at /opt/njit-advisor/venv"
    exit 1
fi

# Activate virtual environment
source /opt/njit-advisor/venv/bin/activate || {
    echo "❌ Could not activate virtual environment"
    exit 1
}

echo "✅ Virtual environment activated"

# Stop the service
echo "🛑 Stopping njit-advisor service..."
sudo systemctl stop njit-advisor

# Backup the current database
if [ -f "data/courses.db" ]; then
    echo "💾 Backing up current database..."
    cp data/courses.db data/courses.db.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Database backed up"
else
    echo "ℹ️  No existing database found - will create new one"
fi

# Run the migration script
echo "🔄 Running database migration..."
python3 migrate_database.py

if [ $? -eq 0 ]; then
    echo "✅ Database migration completed successfully"
else
    echo "❌ Database migration failed"
    exit 1
fi

# Update Python dependencies if needed
echo "📦 Checking Python dependencies..."
pip install -r requirements-ec2.txt

# Set proper permissions
echo "🔐 Setting file permissions..."
sudo chown -R njit-advisor:njit-advisor /opt/njit-advisor/app/data/
sudo chmod 755 /opt/njit-advisor/app/data/
sudo chmod 644 /opt/njit-advisor/app/data/*

# Start the service
echo "🚀 Starting njit-advisor service..."
sudo systemctl start njit-advisor

# Check service status
sleep 3
if sudo systemctl is-active --quiet njit-advisor; then
    echo "✅ Service started successfully"
    echo "🌐 Your site should now be working at njitelectiveadvisor.com"
else
    echo "❌ Service failed to start"
    echo "📋 Check logs with: sudo journalctl -u njit-advisor -f"
    echo "📋 Check error logs: sudo tail -f /var/log/njit-advisor/error.log"
    exit 1
fi

# Show service status
echo ""
echo "📊 Service Status:"
sudo systemctl status njit-advisor --no-pager -l

echo ""
echo "✨ Fix completed! Your NJIT Elective Advisor should now be working."
echo "🔍 Monitor logs with: sudo journalctl -u njit-advisor -f"
