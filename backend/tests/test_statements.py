"""
The file contains the test data for database.
This file have been creating like the db/dependencies/base_statements.py file.
"""

from sqlalchemy import insert
from tests.unit.constants import (
    BELARUS_ID,
    MOSCOW_REGION_ID,
    MOSCOW_REGION_NAME,
    RUSSIA_ID,
    SAMARA_REGION_ID,
    SAMARA_REGION_NAME,
)

from db.models import Country, Region
from db.statement import Statement

# Tuple of insert statements for initial **test** data loading
TEST_STATEMENTS: tuple[Statement, ...] = (
    Statement(
        description="Insert country 'Russia'",
        statement=insert(Country),
        data={"country_id": RUSSIA_ID, "name": "Russia"},
        check_query=lambda session: session.query(Country)
        .filter_by(country_id=RUSSIA_ID)
        .first(),
    ),
    Statement(
        description="Insert country 'Belarus'",
        statement=insert(Country),
        data={"country_id": BELARUS_ID, "name": "Belarus"},
        check_query=lambda session: session.query(Country)
        .filter_by(country_id=BELARUS_ID)
        .first(),
    ),
    Statement(
        description=f"Insert region {SAMARA_REGION_NAME}",
        statement=insert(Region),
        data={
            "region_id": SAMARA_REGION_ID,
            "country_id": RUSSIA_ID,
            "name": SAMARA_REGION_NAME,
        },
        check_query=lambda session: session.query(Region)
        .filter_by(country_id=RUSSIA_ID)
        .first(),
    ),
    Statement(
        description=f"Insert region {MOSCOW_REGION_NAME}",
        statement=insert(Region),
        data={
            "region_id": MOSCOW_REGION_ID,
            "country_id": RUSSIA_ID,
            "name": MOSCOW_REGION_NAME,
        },
        check_query=lambda session: session.query(Region)
        .filter_by(country_id=RUSSIA_ID)
        .first(),
    ),
)


def get_test_statements() -> tuple[Statement, ...]:
    """
    Return the base statements for database configuration (for first startup)
    """
    return TEST_STATEMENTS
