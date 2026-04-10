"""Constants used throughout the Octopy Energy API client."""

# API Configuration
DEFAULT_TIMEOUT = 30.0
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 25000

# Retry Configuration
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2.0
RETRY_STATUS_CODES = {408, 429, 500, 502, 503, 504}

# Validation Patterns
API_KEY_PATTERN = r"^sk_(live|test)_[a-zA-Z0-9]+$"
ACCOUNT_NUMBER_PATTERN = r"^A-[A-Z0-9]{8}$"
