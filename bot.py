#!/usr/bin/env python3
"""
Viably Shop Bot - Telegram E-commerce Bot
Created by Viably Template Generator
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database.db import init_db
from handlers import user, admin, cart, checkout

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main bot entry point"""
    # Initialize bot
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Include routers
    dp.include_router(user.router)
    dp.include_router(cart.router)
    dp.include_router(checkout.router)
    dp.include_router(admin.router)

    logger.info("Bot started")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
