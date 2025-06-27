from pytest import fixture, mark
from tests.unit.constants import TEST_COUNTRY_ID, TEST_COUNTRY_NAME

from domain.entities.country import Country


@fixture
def base_country():
    return Country(
        country_id=TEST_COUNTRY_ID,
        name=TEST_COUNTRY_NAME,
    )


class TestCountry:
    @mark.grape
    @mark.country
    @mark.skip(reason="Has't implemented yet.")
    def test_create_country(self, base_country: Country): ...

    @mark.grape
    @mark.country
    @mark.skip(reason="Has't implemented yet.")
    def test_get_contry(self, base_country: Country): ...

    @mark.grape
    @mark.country
    @mark.skip(reason="Has't implemented yet.")
    def test_update_country(self, base_country: Country): ...

    @mark.grape
    @mark.country
    @mark.skip(reason="Has't implemented yet.")
    def test_delete_country(self, base_country: Country): ...
