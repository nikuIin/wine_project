"""
The file contains the test data for database.
This file have been creating like the db/dependencies/base_statements.py file.
"""

from sqlalchemy import insert

from db.models import Country
from db.statement import Statement

# Tuple of insert statements for initial **test** data loading
TEST_STATEMENTS: tuple[Statement, ...] = (
    Statement(
        description="Insert country 'Russia'",
        statement=insert(Country),
        data={"country_id": 643, "name": "Russia"},
        check_query=lambda session: session.query(Country)
        .filter_by(country_id=643)
        .first(),
    ),
    Statement(
        description="Insert country 'Belarus'",
        statement=insert(Country),
        data={"country_id": 112, "name": "Belarus"},
        check_query=lambda session: session.query(Country)
        .filter_by(country_id=112)
        .first(),
    ),
)


def get_test_statements() -> tuple[Statement, ...]:
    """
    Return the base statements for database configuration (for first startup)
    """
    return TEST_STATEMENTS
