"""Admin keyboards"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu():
    """Admin menu keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Products"), KeyboardButton(text="📁 Categories")],
            [KeyboardButton(text="📋 Orders"), KeyboardButton(text="📊 Statistics")],
            [KeyboardButton(text="◀️ Back to shop")]
        ],
        resize_keyboard=True
    )


def product_actions(product_id):
    """Product management actions"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Edit", callback_data=f"edit_product:{product_id}")],
            [InlineKeyboardButton(text="🗑 Delete", callback_data=f"delete_product:{product_id}")],
            [InlineKeyboardButton(text="◀️ Back", callback_data="admin_products")]
        ]
    )


def order_actions(order_id):
    """Order management actions"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Confirm", callback_data=f"order_confirm:{order_id}")],
            [InlineKeyboardButton(text="🚚 Ship", callback_data=f"order_ship:{order_id}")],
            [InlineKeyboardButton(text="✔️ Deliver", callback_data=f"order_deliver:{order_id}")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data=f"order_cancel:{order_id}")],
        ]
    )
