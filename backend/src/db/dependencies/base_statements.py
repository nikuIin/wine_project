from sqlalchemy import insert

from db.models import Country, Status
from db.statement import Statement

SCHEMAS_LIST = (
    "ref",
    "crm",
    "auth",
    "catalog",
    "grape",
)

# Tuple of insert statements for initial data loading
# TODO: add statuses, roles and reformat insert country data.
BASE_STATEMENTS: tuple[Statement, ...] = (
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


def get_base_statements() -> tuple[Statement, ...]:
    """
    Return the base statements for database configuration (for first startup)
    """
    return BASE_STATEMENTS
