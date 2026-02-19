"""Configuration settings"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot settings
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///shop.db")

# Payment settings (optional)
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "")

# Shop settings
SHOP_NAME = os.getenv("SHOP_NAME", "My Shop")
CURRENCY = os.getenv("CURRENCY", "USD")
CURRENCY_SYMBOL = os.getenv("CURRENCY_SYMBOL", "$")

# Order settings
SUPPORT_CONTACT = os.getenv("SUPPORT_CONTACT", "@support")
ORDER_NOTIFICATION_CHAT = os.getenv("ORDER_NOTIFICATION_CHAT", "")
