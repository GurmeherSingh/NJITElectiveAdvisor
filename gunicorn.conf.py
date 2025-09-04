# Gunicorn configuration file for NJIT Elective Advisor
# Place this file at /opt/njit-advisor/gunicorn.conf.py

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)  # Cap at 4 workers for t3.micro
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Preload application for better performance
preload_app = True

# Logging
accesslog = "/var/log/njit-advisor/access.log"
errorlog = "/var/log/njit-advisor/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "njit-advisor"

# Server mechanics
daemon = False
pidfile = "/var/run/njit-advisor.pid"
user = "njit-advisor"
group = "njit-advisor"
tmp_upload_dir = None

# SSL (uncomment if using SSL termination at Gunicorn level)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment variables
raw_env = [
    "FLASK_ENV=production",
    "PYTHONPATH=/opt/njit-advisor/app",
]

# Worker timeout for graceful shutdown
graceful_timeout = 30

# Maximum number of pending connections
max_requests_jitter = 100

# Enable stdio inheritance
enable_stdio_inheritance = True

# Capture output
capture_output = True

# Worker process lifecycle
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting NJIT Elective Advisor server")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading NJIT Elective Advisor server")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("NJIT Elective Advisor server is ready. PID: %s", os.getpid())

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing.")

def child_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info("Worker exited (pid: %s)", worker.pid)

def max_requests_jitter_handler(server):
    """Called when max_requests_jitter is reached."""
    server.log.info("Max requests jitter reached, restarting worker")