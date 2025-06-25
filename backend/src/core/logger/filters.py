from logging import Filter


class ColorFilter(Filter):
    """
    Logging filter that adds a 'color' attribute to the log record
    based on the log level, for use in colored log formatting.
    """

    # Dictionary mapping log levels to color names.
    COLOR = {
        "DEBUG": "GREEN",
        "INFO": "GREEN",
        "WARNING": "YELLOW",
        "ERROR": "RED",
        "CRITICAL": "RED",
    }

    def filter(self, record):
        """
        Add a 'color' attribute to the record based on its level name.
        """
        record.color = ColorFilter.COLOR[record.levelname]
        return True


class SensitiveWordsFilter(Filter):
    """
    Logging filter that prevents log messages containing certain
    sensitive words from being processed.
    """

    # Set of words that will cause the log message to be filtered.
    SENSITIVE_WORDS: set[str] = {
        "phone",
        "password",
        "passport",
        "api",
        "key",
    }

    def filter(self, record):
        """
        Check if the log message contains any of the sensitive words.
        Returns False to filter the record if a sensitive word is found.
        """
        return not any(
            word.lower() in str(record.msg).lower() for word in SensitiveWordsFilter.SENSITIVE_WORDS
        )
