from enum import IntEnum, StrEnum


class LanguageEnum(StrEnum):
    DEFAULT_LANGUAGE = "ru-RU"
    RUSSIAN = "ru-RU"
    KAZAKHSTAN = "kz-KZ"
    ENGLISH = "en-US"


class ArticleStatus(IntEnum):
    DRAFT = 1
    DEFERRED = 2
    PUBLISHED = 3


class ArticleCategory(IntEnum):
    RED_WINE = 1
    WHITE_WINE = 2
