from contextlib import nullcontext as dont_raise

from pytest import fixture, mark, raises
from tests.unit.constants import (
    TEST_COUNTRY_ID,
    TEST_COUNTRY_NAME,
    TEST_COUNTRY_NAME_LOW_REGISTRY,
)

from domain.entities.country import Country


@fixture
def base_country():
    return Country(
        country_id=TEST_COUNTRY_ID,
        name=TEST_COUNTRY_NAME,
    )


@fixture
def base_low_name_registry_country():
    return Country(
        country_id=TEST_COUNTRY_ID,
        name=TEST_COUNTRY_NAME_LOW_REGISTRY,
    )


class TestCountry:
    @mark.country
    @mark.parametrize(
        "country_id, name, expectation",
        [
            (1, "Россия", dont_raise()),
            (-2, "Россия", raises(ValueError)),
            ("123", "Россия", dont_raise()),
        ],
    )
    def test_country_create():
        pass

    @mark.country
    def test_create_country_low_registry_name(
        self,
        base_low_name_registry_country: Country,
    ):
        upper_case_name = TEST_COUNTRY_NAME_LOW_REGISTRY.capitalize()
        assert base_low_name_registry_country == Country(
            country_id=TEST_COUNTRY_ID,
            name=upper_case_name,
        )
