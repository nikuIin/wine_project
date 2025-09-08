from pathlib import Path

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.utils.markdown import bold, pre

from core.config import telegram_settings
from core.logger.logger import get_configure_logger
from dto.deal_dto import DealDTO
from telegram.telegram_helper import telegram_helper

logger = get_configure_logger(Path(__file__).stem)


class TelegramNotificationManager:
    def __init__(self, bot: Bot, chat_id: int):
        self._bot = bot
        self._chat_id = chat_id

    @telegram_helper.dispatcher.message()
    async def send_deal_data(
        self,
        deal: DealDTO,
    ):
        text = (
            "Новая заявка:\n\n"
            + f"{bold('ID сделки')} {pre(deal.deal_id)}\n\n"
            + f"{bold('==============')}\n\n"
            + f"{bold('ID ответсвенного менеджера')} {pre(deal.manager_id)}\n"
            + f"{bold('ID клиента')} {pre(deal.lead_id)}\n\n"
            + f"{bold('==============')}\n\n"
            + f"{bold('Стоимость')}: {bold(deal.cost)}\n"
            + f"{bold('Создана')}: {bold(deal.created_at)}\n\n"
            + f"{bold('==============')}\n\n"
        )

        if "email" in deal.fields:
            text += f"{bold('Email')}: {pre(deal.fields['email'])}\n"
        if "phone" in deal.fields:
            text += f"{bold('Телефон')}: {pre(deal.fields['phone'])}\n"
        if "question" in deal.fields:
            text += f"{bold('Вопрос')}: {pre(deal.fields['question'])}\n"

        await self._bot.send_message(
            chat_id=self._chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )


telegram_notification_manager = TelegramNotificationManager(
    bot=telegram_helper.bot,
    chat_id=telegram_settings.deals_chat_id,
)
