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


class ArticleCategoriesID(IntEnum):
    RED_WINE = 1
    WHITE_WINE = 2


class ArticleSortBy(StrEnum):
    # should be named like columns in the article table
    PUBLISHED_AT = "published_at"
    VIEWS_COUNT = "views_count"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class TSQUERYRules(StrEnum):
    AND = "&"
    OR = "|"
    NOT = "!"


class Priority(IntEnum):
    NO_PRIORITY = -1
    HIGHEST_PRIORIRY = 10
