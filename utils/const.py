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
MODAL_CROSS_ENC = r"https://plaxtonflarion--web-app.modal.run/rerank"
MODAL_TENSOR_EN = r"https://plaxtonflarion--web-app.modal.run/tensor/en"
MODAL_TENSOR_ZH = r"https://plaxtonflarion--web-app.modal.run/tensor/zh"
MODAL_PREDICT   = r"https://plaxtonflarion--web-app.modal.run/predict"
MODAL_SERVICE   = r"https://plaxtonflarion--web-app.modal.run/service"

# ---- Notes: 日志 ----
SHOW_LEVEL   = r"INFO"
PRINT_FORMAT = r"<bold><level>{level}</level></bold>: <bold><cyan>{message}</cyan></bold>"
WRITE_FORMAT = r"{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"

# ---- Notes: Application ----
SETTINGS = {
    "title": "AppServerX",
    "description": "AppServerX Application Server",
    "version": "1.0.0",
    "openapi_url": None,
    "docs_url": None,
    "redoc_url": None,
}

# ---- Notes: Redis Token Bucket ----
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

# ---- Notes: Redis Hot Key ----
K_MIX = "Mix"
V_MIX = {
  "app": {
    "Azure": {
      "tts_engine": {
        "enabled": False
      }
    },
    "Modal": {
      "inference": {
        "enabled": True
      }
    },
    "Groq": {
      "llm": {
        "name": "llama-3.1-8b-instant"
    }
  }
  },
  "white_list": [
    "/",
    "/status",
    "/keepalive-render",
    "/keepalive-supabase",
    "/keepalive-modal",
    "/openapi.json",
    "/favicon.ico",
    "/docs",
    "/redoc",
    "/self-heal",
    "/self-heal-stream"
  ],
  "rate_config": {
    "default": {
      "burst": 10,
      "rate": 2,
      "max_wait": 1
    },
    "routes": {
      "/sign": {
        "burst": 2,
        "rate": 0.2
      },
      "/self-heal": {
        "burst": 5,
        "rate": 1
      },
      "/self-heal-stream": {
        "burst": 5,
        "rate": 1
      }
    },
    "ip": {}
  }
}

# ---- Notes: 提示词 ----
R_PROMPT = """
你是 RAG/Embedding 路由器，请根据【用户输入文本】判断最佳检索策略。务必严格按规则输出 JSON。

=== 判断逻辑（必须严格遵守） ===
1. 语言识别：
   - 输入只包含英文字母/符号/数字/下划线/id/class/xpath/css → "en"
   - 输入只包含中文或中文占多数 → "zh"
   - 同时包含中英文比例明显混合 → "union"
   【注意：上下文提示为中文不代表用户输入是中文，判断只依据用户输入文本】

2. Embedding 模型：
   zh → bge-zh
   en → bge-en
   union → bge-m3

3. Search 策略：
   - id/class/xpath/css/token 短字段 → "single"
   - 描述型自然语言（句子形态）→ "dual"

4. rerank_weight：
   - token结构 + 短词 → 0.2~0.4
   - 句子或含语义表达 → 0.7~0.95

=== 用户输入文本（仅看这部分，不要参考其他文字）===
{text}

=== 输出（严格 JSON，不要多余字符）===
{{
  "lang": "...",
  "embedding": "...",
  "search": "...",
  "rerank_weight": ...,
  "reason": "一句话说明原因"
}}

=== 正例 ===
输入: "submit_btn"
输出: {{"lang":"en","embedding":"bge-en","search":"single","rerank_weight":0.3,"reason":"英文token定位词"}}

输入: "支付失败，请重试"
输出: {{"lang":"zh","embedding":"bge-zh","search":"dual","rerank_weight":0.8,"reason":"中文UI文案需要语义召回"}}

输入: "付款失败 Payment Failed"
输出: {{"lang":"union","embedding":"bge-en","search":"dual","rerank_weight":0.8,"reason":"中英文混合语义表达"}}

=== 反例提醒 ===
不要因为本Prompt是中文就判断为 zh
输入包含 id/resource_id/token/xpath 时优先判断为 en
"""
F_PROMPT = """
你是自动化测试中的元素自愈专家。

旧定位：
- by: {by}
- value: {value}

候选列表（已按相似度排序）：
{cand_desc}

请只返回 JSON:
{{
  "index": <整数, -1 表示不选>,
  "reason": "<原因>"
}}
"""


if __name__ == '__main__':
    pass
