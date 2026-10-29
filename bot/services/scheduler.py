"""Scheduler service for automated daily English word and study reminders."""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
import pytz
from bot.config import settings

logger = logging.getLogger(__name__)

def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Initialize APScheduler."""
    tz = pytz.timezone(settings.TIMEZONE)
    scheduler = AsyncIOScheduler(timezone=tz)

    # Could schedule daily reminders or periodic tasks here
    scheduler.start()
    return scheduler
