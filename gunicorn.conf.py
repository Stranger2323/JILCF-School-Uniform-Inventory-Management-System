import multiprocessing

# Bind to 0.0.0.0:$PORT for Render deployment
bind = "0.0.0.0:8080"

# Worker configuration
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# SSL configuration (if needed)
# keyfile = 'path/to/keyfile'
# certfile = 'path/to/certfile'

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
