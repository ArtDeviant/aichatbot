import asyncio
import logging
from django.core.management.base import BaseCommand
from aichat.telegram_bot import setup_telegram_bot

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Telegram bot...'))
        try:
            asyncio.run(setup_telegram_bot())
        except Exception as e:
            logger.exception(f"Error running Telegram bot: {str(e)}")
            self.stdout.write(self.style.ERROR(f"Error running Telegram bot: {str(e)}"))
            raise