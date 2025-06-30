"""The file with constats for the tests"""

from uuid import UUID

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
