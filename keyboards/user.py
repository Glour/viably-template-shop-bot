"""User keyboards"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu():
    """Main menu keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Catalog"), KeyboardButton(text="🛒 Cart")],
            [KeyboardButton(text="📦 My Orders"), KeyboardButton(text="ℹ️ Info")]
        ],
        resize_keyboard=True
    )


def categories_keyboard(categories):
    """Categories selection keyboard"""
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(
            text=f"{category.emoji} {category.name}",
            callback_data=f"category:{category.id}"
        )
    builder.adjust(2)
    return builder.as_markup()


def products_keyboard(products, category_id):
    """Products in category keyboard"""
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(
            text=f"{product.name} - ${product.price}",
            callback_data=f"product:{product.id}"
        )
    builder.button(text="◀️ Back to categories", callback_data="categories")
    builder.adjust(1)
    return builder.as_markup()


def product_detail_keyboard(product_id, in_cart=False):
    """Product detail keyboard"""
    builder = InlineKeyboardBuilder()
    if not in_cart:
        builder.button(text="➕ Add to cart", callback_data=f"add_cart:{product_id}")
    else:
        builder.button(text="➖ Remove from cart", callback_data=f"remove_cart:{product_id}")
    builder.button(text="◀️ Back", callback_data="back_to_products")
    builder.adjust(1)
    return builder.as_markup()


def cart_keyboard(has_items=True):
    """Cart keyboard"""
    builder = InlineKeyboardBuilder()
    if has_items:
        builder.button(text="✅ Checkout", callback_data="checkout")
        builder.button(text="🗑 Clear cart", callback_data="clear_cart")
    builder.button(text="◀️ Continue shopping", callback_data="categories")
    builder.adjust(1)
    return builder.as_markup()


def confirm_order_keyboard():
    """Confirm order keyboard"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Confirm order", callback_data="confirm_order")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_order")]
        ]
    )
