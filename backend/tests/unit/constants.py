"""The file with constats for the tests"""

from uuid import UUID

from uuid_extensions import uuid7

from domain.enums import LanguageEnum

# Roles
USER_ROLE = 1
ADMIN_ROLE = 2
NO_EXISTING_ROLE = 100

# The data for product
TEST_PRODUCT_UUID = UUID("a5e7d95f-3f06-4a31-8079-4f9c937f4775")
TEST_PRODUCT_NAME = "Cute product"
TEST_PRODUCT_PRICE = 100.50
TEST_RPODUCT_BRAND_ID = 1
TEST_PRODUCT_DISCOUNT = 0.2

# Country data
TEST_COUNTRY_ID = 1
TEST_COUNTRY_NAME = "Cool country"
TEST_COUNTRY_NAME_LOW_REGISTRY = "low registry country name"

# country prepared data
RUSSIA_ID = 643
RUSSIA_NAME = "Russian Federation"

BELARUS_ID = 112
BELARUS_NAME = "Belaruss"

NO_EXISTING_COUNTRY_ID = 999

# New region (for creating, updating tests)
NEW_REGION_ID = 1
NEW_REGION_NAME = "New region"
NEW_REGION_COUNTRY_ID = RUSSIA_ID

# region prepared data
SAMARA_REGION_ID = 63
SAMARA_REGION_NAME = "Samara"
SAMARA_REGION_COUNTRY_ID = RUSSIA_ID

MOSCOW_REGION_ID = 77
MOSCOW_REGION_NAME = "Moscow"
MOSCOW_REGION_COUNTRY_ID = RUSSIA_ID

# no existing region
NO_EXISTING_REGION_ID = 9999

# no existing language
NO_EXISTING_LANGUAGE = "no_existing_language"


# Grape constants

# this grape will creating only in tests
BASE_GRAPE_UUID = UUID("06868f0a-789b-7163-8000-dc8d41f77ad4")
BASE_GRAPE_REGION_ID = SAMARA_REGION_ID

BASE_GRAPE_NAME_EN = "Base grape"
BASE_GRAPE_NAME_RU = "Базовый виноград"

# this grape will create before tests
PINOT_GRAPE_ID = UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
PINOT_GRAPE_NAME = "Pinot noir"
PINOT_GRAPE_REGION_ID = MOSCOW_REGION_ID
PINOT_GRAPE_LANGUAGE = LanguageEnum.RUSSIAN

NO_EXISTING_GRAPE_ID = UUID("3fa85f64-5717-4562-b4fc-2c963f66afa6")

# new grape data
NEW_GRAPE_ID = UUID("3fa85f64-5717-4562-b4fc-2c963f66afa7")
NEW_GRAPE_NAME = "New grape"
NEW_GRAPE_REGION_ID = MOSCOW_REGION_ID
NEW_GRAPE_LANGUAGE = LanguageEnum.RUSSIAN


# For auth_code_repository
REDIS_TEST_USER_ID = uuid7()
REDIS_TEST_EMAIL = "test@mail.ru"
REDIS_TEST_CODE = "123456"
