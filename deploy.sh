#!/bin/bash

# NJIT Elective Advisor - EC2 Deployment Script
# This script automates the deployment and update process

set -e  # Exit on any error

# Configuration
APP_DIR="/opt/njit-advisor"
APP_USER="njit-advisor"
SERVICE_NAME="njit-advisor"
LOG_DIR="/var/log/njit-advisor"
REPO_URL="https://github.com/GurmeherSingh/NJITElectiveAdvisor.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Please run as a regular user with sudo privileges."
        exit 1
    fi
}

# Check if user has sudo privileges
check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        error "This script requires sudo privileges. Please ensure your user can run sudo commands."
        exit 1
    fi
}

# Create application user if it doesn't exist
create_user() {
    log "Creating application user..."
    if ! id "$APP_USER" &>/dev/null; then
        sudo adduser --system --group --home "$APP_DIR" "$APP_USER"
        success "Created user: $APP_USER"
    else
        log "User $APP_USER already exists"
    fi
}

# Create directories
create_directories() {
    log "Creating directories..."
    sudo mkdir -p "$APP_DIR"
    sudo mkdir -p "$LOG_DIR"
    sudo chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    sudo chown -R "$APP_USER:$APP_USER" "$LOG_DIR"
    success "Directories created"
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    sudo apt update
    sudo apt install -y python3.10 python3.10-venv python3-pip nginx git curl
    success "System dependencies installed"
}

# Clone or update repository
setup_repository() {
    log "Setting up repository..."
    if [ -d "$APP_DIR/app" ]; then
        log "Updating existing repository..."
        cd "$APP_DIR/app"
        sudo -u "$APP_USER" git fetch origin
        sudo -u "$APP_USER" git reset --hard origin/main
        success "Repository updated"
    else
        log "Cloning repository..."
        sudo -u "$APP_USER" git clone "$REPO_URL" "$APP_DIR/app"
        success "Repository cloned"
    fi
}

# Setup virtual environment
setup_venv() {
    log "Setting up virtual environment..."
    if [ ! -d "$APP_DIR/venv" ]; then
        sudo -u "$APP_USER" python3.10 -m venv "$APP_DIR/venv"
    fi
    
    sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --upgrade pip
    sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/app/requirements-ec2.txt"
    success "Virtual environment setup complete"
}

# Setup database
setup_database() {
    log "Setting up database..."
    cd "$APP_DIR/app"
    sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" setup_data.py
    success "Database setup complete"
}

# Install configuration files
install_configs() {
    log "Installing configuration files..."
    
    # Copy Gunicorn config
    sudo cp "$APP_DIR/app/gunicorn.conf.py" "$APP_DIR/"
    sudo chown "$APP_USER:$APP_USER" "$APP_DIR/gunicorn.conf.py"
    
    # Copy systemd service
    sudo cp "$APP_DIR/app/njit-advisor.service" "/etc/systemd/system/"
    sudo systemctl daemon-reload
    
    # Copy Nginx config
    sudo cp "$APP_DIR/app/nginx.conf" "/etc/nginx/sites-available/njit-advisor"
    sudo ln -sf "/etc/nginx/sites-available/njit-advisor" "/etc/nginx/sites-enabled/"
    sudo rm -f /etc/nginx/sites-enabled/default
    
    success "Configuration files installed"
}

# Start services
start_services() {
    log "Starting services..."
    
    # Test Nginx configuration
    sudo nginx -t
    if [ $? -eq 0 ]; then
        sudo systemctl restart nginx
        sudo systemctl enable nginx
        success "Nginx started and enabled"
    else
        error "Nginx configuration test failed"
        exit 1
    fi
    
    # Start application service
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl restart "$SERVICE_NAME"
    
    # Wait a moment and check status
    sleep 3
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        success "Application service started"
    else
        error "Failed to start application service"
        sudo systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

# Setup firewall
setup_firewall() {
    log "Setting up firewall..."
    sudo ufw --force enable
    sudo ufw allow ssh
    sudo ufw allow 'Nginx Full'
    success "Firewall configured"
}

# Display status
show_status() {
    log "Deployment Status:"
    echo "=================="
    
    # Service status
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        success "Application: Running"
    else
        error "Application: Not running"
    fi
    
    if sudo systemctl is-active --quiet nginx; then
        success "Nginx: Running"
    else
        error "Nginx: Not running"
    fi
    
    # Show logs
    echo ""
    log "Recent application logs:"
    sudo journalctl -u "$SERVICE_NAME" --no-pager -n 10
    
    echo ""
    log "Application URL: http://$(curl -s ifconfig.me)"
    log "Logs location: $LOG_DIR"
    log "Application directory: $APP_DIR"
}

# Update application
update_app() {
    log "Updating application..."
    
    # Stop service
    sudo systemctl stop "$SERVICE_NAME"
    
    # Update code
    cd "$APP_DIR/app"
    sudo -u "$APP_USER" git pull origin main
    
    # Update dependencies
    sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install -r requirements-ec2.txt
    
    # Restart service
    sudo systemctl start "$SERVICE_NAME"
    
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        success "Application updated successfully"
    else
        error "Failed to update application"
        sudo systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

# Main deployment function
deploy() {
    log "Starting deployment of NJIT Elective Advisor..."
    
    check_root
    check_sudo
    create_user
    create_directories
    install_dependencies
    setup_repository
    setup_venv
    setup_database
    install_configs
    start_services
    setup_firewall
    show_status
    
    success "Deployment completed successfully!"
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "update")
        update_app
        ;;
    "status")
        show_status
        ;;
    "logs")
        sudo journalctl -u "$SERVICE_NAME" -f
        ;;
    "restart")
        sudo systemctl restart "$SERVICE_NAME"
        success "Application restarted"
        ;;
    "stop")
        sudo systemctl stop "$SERVICE_NAME"
        success "Application stopped"
        ;;
    "start")
        sudo systemctl start "$SERVICE_NAME"
        success "Application started"
        ;;
    *)
        echo "Usage: $0 {deploy|update|status|logs|restart|stop|start}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Full deployment (default)"
        echo "  update  - Update application code and dependencies"
        echo "  status  - Show application status"
        echo "  logs    - Follow application logs"
        echo "  restart - Restart application"
        echo "  stop    - Stop application"
        echo "  start   - Start application"
        exit 1
        ;;
esac