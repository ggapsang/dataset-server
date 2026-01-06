import os

# Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/Alias_Storage.db")
NGINX_BASE_URL = os.getenv("NGINX_BASE_URL", "http://nginx")
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "1000"))
