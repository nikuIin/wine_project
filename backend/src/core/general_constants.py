"""
The file with the general constants of the project.
It means, that this file contains only constants, that can be used
by the several files. If the file/module have constants and
this constants are used only in this file/module, it's ok, if
they are provides in those file/module.

Examples:
The STR_LENGTH is the general constant, what doesn't concern to the PASSWORD_CONTEXT.
"""

# Schemas and models
BASE_MIN_STR_LENGTH = 1
BASE_MAX_STR_LENGTH = 255

MAX_MESSAGE_LENGTH = 4096
MIN_DB_INT = -2147483648
MAX_DB_INT = 2147483647

MAX_COUNTRY_ID = 999

MAX_LIMIT = 100
DEFAULT_LIMIT = 12

ONE_HOUR_IN_SECONDS = 3600
HALF_AN_HOUR_IN_SECONDS = 1800
FIFTEEN_MINUTES_IN_SECONDS = 900

# Auth constants
# ==================
# auth verification code
CODE_LEN = 6
CODE_LE_VALUE = 1_000_000  # it's mean, the max code is 999-999
CODE_REQUEST_LOCK_TIME_IN_SECONDS = 60


RUSSIAN_LOWERCASE_LETTERS = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
