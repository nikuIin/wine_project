from pathlib import Path

from aiogram import Bot, Dispatcher

from core.config import telegram_settings
from core.logger.logger import get_configure_logger

logger = get_configure_logger(Path(__file__).stem)


class TelegramHelper:
    def __init__(self):
        self._bot = Bot(telegram_settings.telegram_bot_token)
        self._dispatcher = Dispatcher()

    @property
    def dispatcher(self):
        return self._dispatcher

    @property
    def bot(self):
        return self._bot


telegram_helper = TelegramHelper()
