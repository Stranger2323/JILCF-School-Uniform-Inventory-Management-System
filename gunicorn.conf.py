import multiprocessing
import os

# Bind to PORT provided by Render
port = int(os.environ.get("PORT", 10000))
bind = f"0.0.0.0:{port}"

# Worker configuration
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'gunicorn_feather_login'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL cert and key files
# certfile = 'fullchain.pem'
# keyfile = 'privkey.pem'
