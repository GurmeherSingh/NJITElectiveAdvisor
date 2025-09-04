# EC2 Deployment Guide for NJIT Elective Advisor

## Prerequisites
- AWS account with EC2 access
- Domain name (optional, for custom domain)
- SSH key pair

## Step 1: Launch EC2 Instance

### Instance Configuration
- **AMI**: Ubuntu 22.04 LTS (Free tier eligible)
- **Instance Type**: t3.micro (Free tier) or t3.small for better performance
- **Storage**: 20-30 GB EBS volume
- **Security Group**: 
  - SSH (22) - Your IP only
  - HTTP (80) - 0.0.0.0/0
  - HTTPS (443) - 0.0.0.0/0 (if using SSL)
  - Custom (5000) - 0.0.0.0/0 (for direct Flask access during setup)

## Step 2: Connect to Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

## Step 3: System Setup

### Update system packages
```bash
sudo apt update && sudo apt upgrade -y
```

### Install Python 3.10 and pip
```bash
sudo apt install python3.10 python3.10-venv python3-pip nginx git -y
```

### Create application user
```bash
sudo adduser --system --group --home /opt/njit-advisor njit-advisor
```

## Step 4: Deploy Application

### Clone repository
```bash
sudo -u njit-advisor git clone https://github.com/GurmeherSingh/NJITElectiveAdvisor.git /opt/njit-advisor/app
cd /opt/njit-advisor/app
```

### Create virtual environment
```bash
sudo -u njit-advisor python3.10 -m venv /opt/njit-advisor/venv
sudo -u njit-advisor /opt/njit-advisor/venv/bin/pip install --upgrade pip
```

### Install dependencies
```bash
sudo -u njit-advisor /opt/njit-advisor/venv/bin/pip install -r requirements.txt
```

### Set up database
```bash
sudo -u njit-advisor /opt/njit-advisor/venv/bin/python setup_data.py
```

## Step 5: Configure Gunicorn

### Create Gunicorn configuration
```bash
sudo nano /opt/njit-advisor/gunicorn.conf.py
```

Add the following content:
```python
bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

## Step 6: Create Systemd Service

Create the service file:
```bash
sudo nano /etc/systemd/system/njit-advisor.service
```

Add the following content:
```ini
[Unit]
Description=NJIT Elective Advisor
After=network.target

[Service]
Type=notify
User=njit-advisor
Group=njit-advisor
WorkingDirectory=/opt/njit-advisor/app
Environment=PATH=/opt/njit-advisor/venv/bin
ExecStart=/opt/njit-advisor/venv/bin/gunicorn --config /opt/njit-advisor/gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and start service
```bash
sudo systemctl daemon-reload
sudo systemctl enable njit-advisor
sudo systemctl start njit-advisor
sudo systemctl status njit-advisor
```

## Step 7: Configure Nginx

### Create Nginx configuration
```bash
sudo nano /etc/nginx/sites-available/njit-advisor
```

Add the following content:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Replace with your domain or EC2 public IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/njit-advisor/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
```

### Enable the site
```bash
sudo ln -s /etc/nginx/sites-available/njit-advisor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 8: SSL Certificate (Optional but Recommended)

### Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Get SSL certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Step 9: Firewall Configuration

### Configure UFW
```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

## Step 10: Monitoring and Logs

### View application logs
```bash
sudo journalctl -u njit-advisor -f
```

### View Nginx logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Step 11: Auto-deployment Script

Create a deployment script for easy updates:
```bash
sudo nano /opt/njit-advisor/deploy.sh
```

Make it executable:
```bash
sudo chmod +x /opt/njit-advisor/deploy.sh
```

## Maintenance Commands

### Restart application
```bash
sudo systemctl restart njit-advisor
```

### Update application
```bash
cd /opt/njit-advisor/app
sudo -u njit-advisor git pull
sudo -u njit-advisor /opt/njit-advisor/venv/bin/pip install -r requirements.txt
sudo systemctl restart njit-advisor
```

### Check service status
```bash
sudo systemctl status njit-advisor
sudo systemctl status nginx
```

## Troubleshooting

### Common Issues

1. **Port 5000 not accessible**: Check security group settings
2. **Service won't start**: Check logs with `sudo journalctl -u njit-advisor`
3. **Database errors**: Ensure database file has correct permissions
4. **Static files not loading**: Check Nginx configuration and file paths

### Performance Optimization

1. **Increase workers**: Edit gunicorn.conf.py and increase `workers` value
2. **Enable caching**: Configure Redis for session storage
3. **Database optimization**: Consider PostgreSQL for production
4. **CDN**: Use CloudFront for static assets

## Security Considerations

1. **Regular updates**: Keep system packages updated
2. **Firewall**: Only open necessary ports
3. **SSL**: Always use HTTPS in production
4. **Backups**: Regular database and file backups
5. **Monitoring**: Set up CloudWatch or similar monitoring

## Cost Optimization

1. **Instance sizing**: Start with t3.micro, scale as needed
2. **Reserved instances**: For long-term deployments
3. **Spot instances**: For development/testing
4. **Auto-scaling**: Configure based on traffic patterns