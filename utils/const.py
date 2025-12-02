#    ____                _
#   / ___|___  _ __  ___| |_
#  | |   / _ \| '_ \/ __| __|
#  | |__| (_) | | | \__ \ |_
#   \____\___/|_| |_|___/\__|
#

# ---- Notes: 格式 ----
CHARSET       = r"UTF-8"
READ_KEY_MODE = r"rb"

# ---- Notes: 密钥 ----
KEYS_DIR         = r"keys"
BASE_PRIVATE_KEY = r"private_key.pem"
BASE_PUBLIC_KEY  = r"public_key.pem"
APP_PRIVATE_KEY  = f"app_{BASE_PRIVATE_KEY}"
APP_PUBLIC_KEY   = f"app_{BASE_PUBLIC_KEY}"

# ---- Notes: 模版 ----
TEMPLATES = r"templates"

# ---- Notes: 配置 ----
CONFIGURATION = r"configuration.json"

# ---- Notes: Supabase ----
SUPABASE_URL  = r"SUPABASE_URL"
SUPABASE_KEY  = r"SUPABASE_KEY"
LICENSE_CODES = r"license_codes"

# ---- Notes: Azure ----
AZURE_TTS_URL = r"AZURE_TTS_URL"
AZURE_TTS_KEY = r"AZURE_TTS_KEY"

# ---- Notes: Redis ----
REDIS_CACHE_URL = r"REDIS_CACHE_URL"
REDIS_CACHE_KEY = r"REDIS_CACHE_KEY"

# ---- Notes: Cloudflare ----
BUCKET        = r"appserver-bucket"
R2_BUCKET_KEY = r"R2_BUCKET_KEY"
R2_BUCKET_USR = r"R2_BUCKET_USR"
R2_BUCKET_PWD = r"R2_BUCKET_PWD"
R2_BUCKET_URL = r"R2_BUCKET_URL"
R2_PUBLIC_URL = r"R2_PUBLIC_URL"

# ---- Notes: 共享密钥 ----
SHARED_SECRET = r"SHARED_SECRET"

# ---- Notes: 鉴权格式 ----
TOKEN_FORMAT = r"X-Token"

# ---- Notes: 日志 ----
SHOW_LEVEL   = r"INFO"
PRINT_FORMAT = r"<bold><level>{level}</level></bold>: <bold><cyan>{message}</cyan></bold>"
WRITE_FORMAT = r"{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"


if __name__ == '__main__':
    pass
