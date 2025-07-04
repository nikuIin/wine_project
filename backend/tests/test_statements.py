"""
The file contains the test data for database.
This file have been creating like the db/dependencies/base_statements.py file.
"""

from sqlalchemy import insert
from tests.unit.constants import (
    BELARUS_ID,
    BELARUS_NAME,
    MOSCOW_REGION_ID,
    MOSCOW_REGION_NAME,
    RUSSIA_ID,
    RUSSIA_NAME,
    SAMARA_REGION_ID,
    SAMARA_REGION_NAME,
)

from db.models import (
    Country,
    CountryTranslate,
    Language,
    Region,
    RegionTranslate,
)
from db.statement import Statement
from domain.enums import LanguageEnum

# Tuple of insert statements for initial **test** data loading
TEST_STATEMENTS: tuple[Statement, ...] = (
    Statement(
        description="Insert language 'ru'",
        statement=insert(Language),
        data={"language_id": LanguageEnum.RUSSIAN, "name": "Russian"},
        check_query=lambda session: session.query(Language)
        .filter_by(language_id=LanguageEnum.RUSSIAN)
        .first(),
    ),
    Statement(
        description="Insert language 'ge'",
        statement=insert(Language),
        data={"language_id": LanguageEnum.GERMAN, "name": "German"},
        check_query=lambda session: session.query(Language)
        .filter_by(language_id=LanguageEnum.GERMAN)
        .first(),
    ),
    Statement(
        description="Insert country 'Russia'",
        statement=insert(Country),
        data={"country_id": RUSSIA_ID},
        check_query=lambda session: session.query(Country)
        .filter_by(country_id=RUSSIA_ID)
        .first(),
    ),
    Statement(
        description="Insert country 'Belarus'",
        statement=insert(Country),
        data={"country_id": BELARUS_ID},
        check_query=lambda session: session.query(Country)
        .filter_by(country_id=BELARUS_ID)
        .first(),
    ),
    Statement(
        description="Insert translate country data 'Belarus'",
        statement=insert(CountryTranslate),
        data={
            "country_id": BELARUS_ID,
            "name": BELARUS_NAME,
            "language_id": LanguageEnum.RUSSIAN,
        },
        check_query=lambda session: session.query(CountryTranslate)
        .filter_by(country_id=BELARUS_ID)
        .first(),
    ),
    Statement(
        description="Insert translate country data 'Belarus'",
        statement=insert(CountryTranslate),
        data={
            "country_id": RUSSIA_ID,
            "name": RUSSIA_NAME,
            "language_id": LanguageEnum.RUSSIAN,
        },
        check_query=lambda session: session.query(CountryTranslate)
        .filter_by(country_id=BELARUS_ID)
        .first(),
    ),
    Statement(
        description="Insert region 'Samara'",
        statement=insert(Region),
        data={"country_id": RUSSIA_ID, "region_id": SAMARA_REGION_ID},
        check_query=lambda session: session.query(Region)
        .filter_by(region_id=SAMARA_REGION_ID)
        .first(),
    ),
    Statement(
        description="Insert region 'Moscow'",
        statement=insert(Region),
        data={"country_id": RUSSIA_ID, "region_id": MOSCOW_REGION_ID},
        check_query=lambda session: session.query(Region)
        .filter_by(region_id=MOSCOW_REGION_ID)
        .first(),
    ),
    Statement(
        description="Insert region transalate data 'Samara'",
        statement=insert(RegionTranslate),
        data={
            "name": SAMARA_REGION_NAME,
            "region_id": SAMARA_REGION_ID,
            "language_id": LanguageEnum.RUSSIAN,
        },
        check_query=lambda session: session.query(RegionTranslate)
        .filter_by(region_id=SAMARA_REGION_ID)
        .first(),
    ),
    Statement(
        description="Insert region transalate data 'Moscow'",
        statement=insert(RegionTranslate),
        data={
            "name": MOSCOW_REGION_NAME,
            "region_id": MOSCOW_REGION_ID,
            "language_id": LanguageEnum.RUSSIAN,
        },
        check_query=lambda session: session.query(RegionTranslate)
        .filter_by(region_id=MOSCOW_REGION_ID)
        .first(),
    ),
)


def get_test_statements() -> tuple[Statement, ...]:
    """
    Return the base statements for database configuration (for first startup)
    """
    return TEST_STATEMENTS
