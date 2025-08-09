from pytest import fixture, mark

from services.article_service import ArticleService


@fixture
def article_service_without_repo():
    return ArticleService(article_repository=None)  # type: ignore


@mark.article
@mark.service
class TestArticleService:
    @mark.parametrize(
        "input_text, expectation_set",
        [
            # Default strings
            ("my cute text", {"my", "cute", "text"}),
            ("Hello World", {"hello", "world"}),
            # Extra spaces
            ("    my    cute    text   ", {"my", "cute", "text"}),
            ("my     text", {"my", "text"}),
            ("\t\n my \t text \n", {"my", "text"}),
            # Only spaces or empty string
            ("", set()),
            ("   ", set()),
            ("\t\n ", set()),
            # Punctuation symbols
            ("my, cute. text!", {"my", "cute", "text"}),
            ("my-cute_text", {"my", "cute", "text"}),
            ("my...cute,,text", {"my", "cute", "text"}),
            # Special symbols
            ("my@#$cute^&*text", {"my", "cute", "text"}),
            ("my!@#cute$text%", {"my", "cute", "text"}),
            # Digits
            ("article 123 text", {"article", "123", "text"}),
            ("123 456", {"123", "456"}),
            # Single word (could be with extra spaces)
            ("single", {"single"}),
            ("   single   ", {"single"}),
            # Mixed cases
            ("my CUTE text!!!", {"my", "cute", "text"}),
            ("My_Cute-Text 123", {"my", "cute", "text", "123"}),
            # Repeated words
            ("my my my text text", {"my", "text"}),
            ("a b c d e f g", {"a", "b", "c", "d", "e", "f", "g"}),
            # Unicode and no-ASCII symbols
            ("привет мир", {"привет", "мир"}),
            ("café olé", {"caf", "ol"}),
            # Полностью из знаков препинания
            ("!@#$%^&*()", set()),
            (",.;:", set()),
        ],
    )
    def test_get_prepared_to_tsquery_text(
        self,
        article_service_without_repo: ArticleService,
        input_text: str,
        expectation_set: set[str],
    ):
        sut = article_service_without_repo._get_searched_words

        words_set = sut(input_text)

        assert expectation_set == words_set
