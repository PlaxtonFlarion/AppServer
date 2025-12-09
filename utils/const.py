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

# ---- Notes: Zilliz Cloud ----
ZILLIZ_URL = r"ZILLIZ_URL"
ZILLIZ_KEY = r"ZILLIZ_KEY"

# ---- Notes: GROQ ----
GROQ_LLM_KEY = r"GROQ_LLM_KEY"

# ---- Notes: 共享密钥 ----
SHARED_SECRET = r"SHARED_SECRET"

# ---- Notes: 鉴权格式 ----
TOKEN_FORMAT = r"X-Token"

# ---- Notes: Modal Apps ----
MODAL_TENSOR  = r"https://plaxtonflarion--apps-embeddingservice-tensor.modal.run"
MODAL_RERANK  = r"https://plaxtonflarion--apps-embeddingservice-rerank.modal.run"
MODAL_PREDICT = r"https://plaxtonflarion--apps-inferenceservice-predict.modal.run"
MODAL_SERVICE = r"https://plaxtonflarion--apps-inferenceservice-service.modal.run"

# ---- Notes: 日志 ----
SHOW_LEVEL   = r"INFO"
PRINT_FORMAT = r"<bold><level>{level}</level></bold>: <bold><cyan>{message}</cyan></bold>"
WRITE_FORMAT = r"{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"

# ---- Notes: 应用 ----
SETTINGS = {
    "title": "AppServerX",
    "description": "AppServerX Application Server",
    "version": "1.0.0",
    "openapi_url": None,
    "docs_url": None,
    "redoc_url": None,
}

# ---- Notes: 白名单 ----
PUBLIC_PATHS = {
    "/",
    "/status",
    "/keepalive-render",
    "/keepalive-supabase",
    "/keepalive-modal",
    "/openapi.json",
    "/favicon.ico",
    "/docs",
    "/redoc"
}

# ---- Notes: 令牌桶 ----
TOKEN_BUCKET_LUA = """
local key   = KEYS[1]
local burst = tonumber(ARGV[1])
local rate  = tonumber(ARGV[2])
local now   = tonumber(ARGV[3])

local data = redis.call("HMGET", key, "tokens", "time")
local tokens = tonumber(data[1])
local last   = tonumber(data[2])

if tokens == nil then
    tokens = burst
    last   = now
else
    local delta = (now - last) / 1000.0
    if delta > 0 then
        tokens = math.min(burst, tokens + delta * rate)
    end
end

if tokens >= 1 then
    tokens = tokens - 1
    redis.call("HMSET", key, "tokens", tokens, "time", now)
    redis.call("EXPIRE", key, math.ceil(burst/rate)+2)
    return tokens
else
    return -1
end
"""

# ---- Notes: 限流 ----
RATE_CONFIG = {
    "default": {
        "burst"    : 10,
        "rate"     : 2,
        "max_wait" : 1
    },
    "routes": {
        "/sign": {
            "burst" : 2,
            "rate"  : 0.2
        },
        "/self-heal": {
            "burst" : 5,
            "rate"  : 1
        },
        "/self-heal-stream": {
            "burst": 5,
            "rate": 1
        }
    },
    "ip": {}
}

# ---- Notes: Redis Key ----
MIX = "Mix"


if __name__ == '__main__':
    pass
