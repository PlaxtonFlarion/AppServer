#    ____                _
#   / ___|___  _ __  ___| |_
#  | |   / _ \| '_ \/ __| __|
#  | |__| (_) | | | \__ \ |_
#   \____\___/|_| |_|___/\__|
#

CHARSET          = r"UTF-8"
READ_KEY_MODE    = r"rb"

KEYS_DIR         = r"keys"

SUPABASE_URL     = r"SUPABASE_URL"
SUPABASE_KEY     = r"SUPABASE_KEY"

CRON_JOB_URL     = r"CRON_JOB_URL"
CRON_JOB_KEY     = r"CRON_JOB_KEY"

APP_FX = {
    "app": "framix",
    "private_key": "framix_private_key.pem",
    "table": {
        "license": "framix_license_codes",
    }
}

APP_MX = {
    "app": "memrix",
    "private_key": "memrix_private_key.pem",
    "table": {
        "license": "memrix_license_codes",
    }
}
