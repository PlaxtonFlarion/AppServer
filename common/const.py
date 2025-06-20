#    ____                _
#   / ___|___  _ __  ___| |_
#  | |   / _ \| '_ \/ __| __|
#  | |__| (_) | | | \__ \ |_
#   \____\___/|_| |_|___/\__|
#

CHARSET            = r"UTF-8"
READ_KEY_MODE      = r"rb"

KEYS_DIR           = r"keys"
BASE_PRIVATE_KEY   = r"private_key.pem"
BASE_PUBLIC_KEY    = r"public_key.pem"
APP_PRIVATE_KEY    = f"app_{BASE_PRIVATE_KEY}"
APP_PUBLIC_KEY     = f"app_{BASE_PUBLIC_KEY}"

TEMPLATES          = r"templates"
TEMPLATE_VERSION   = r"version_template.json"

SUPABASE_URL       = r"SUPABASE_URL"
SUPABASE_KEY       = r"SUPABASE_KEY"
LICENSE_CODES      = r"license_codes"

CRON_JOB_URL       = r"CRON_JOB_URL"
CRON_JOB_KEY       = r"CRON_JOB_KEY"
FOLDER_ID          = 47245

AZURE_TTS_URL      = r"AZURE_TTS_URL"
AZURE_TTS_KEY      = r"AZURE_TTS_KEY"

REDIS_CACHE_URL    = r"REDIS_CACHE_URL"
REDIS_CACHE_KEY    = r"REDIS_CACHE_KEY"

ACTIVATION_URL     = r"ACTIVATION_URL"

SHOW_LEVEL         = r"INFO"
PRINT_FORMAT       = r"<bold><level>{level}</level></bold>: <bold><cyan>{message}</cyan></bold>"
WRITE_FORMAT       = r"{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"


if __name__ == '__main__':
    pass
