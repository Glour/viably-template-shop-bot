"""Cart handlers"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, delete

from database.db import SessionLocal, CartItem, Product
from keyboards.user import cart_keyboard
from config import CURRENCY_SYMBOL

router = Router()


@router.message(F.text == "🛒 Cart")
async def show_cart(message: Message):
    """Show user's cart"""
    await _display_cart(message.from_user.id, message)


@router.callback_query(F.data.startswith("add_cart:"))
async def add_to_cart(callback: CallbackQuery):
    """Add product to cart"""
    product_id = int(callback.data.split(":")[1])
    
    async with SessionLocal() as session:
        product = await session.get(Product, product_id)
        if not product or not product.is_active:
            await callback.answer("Product not available", show_alert=True)
            return
        
        if product.stock <= 0:
            await callback.answer("Product out of stock", show_alert=True)
            return
        
        # Check if already in cart
        result = await session.execute(
            select(CartItem).where(
                CartItem.user_id == callback.from_user.id,
                CartItem.product_id == product_id
            )
        )
        cart_item = result.scalar_one_or_none()
        
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(
                user_id=callback.from_user.id,
                product_id=product_id,
                quantity=1
            )
            session.add(cart_item)
        
        await session.commit()
    
    await callback.answer(f"✅ {product.name} added to cart!", show_alert=False)
    
    # Update keyboard to show "Remove from cart"
    from keyboards.user import product_detail_keyboard
    try:
        await callback.message.edit_reply_markup(
            reply_markup=product_detail_keyboard(product_id, in_cart=True)
        )
    except:
        pass


@router.callback_query(F.data.startswith("remove_cart:"))
async def remove_from_cart(callback: CallbackQuery):
    """Remove product from cart"""
    product_id = int(callback.data.split(":")[1])
    
    async with SessionLocal() as session:
        await session.execute(
            delete(CartItem).where(
                CartItem.user_id == callback.from_user.id,
                CartItem.product_id == product_id
            )
        )
        await session.commit()
    
    await callback.answer("🗑 Removed from cart")
    
    # Update keyboard
    from keyboards.user import product_detail_keyboard
    try:
        await callback.message.edit_reply_markup(
            reply_markup=product_detail_keyboard(product_id, in_cart=False)
        )
    except:
        pass


@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    """Clear entire cart"""
    async with SessionLocal() as session:
        await session.execute(
            delete(CartItem).where(CartItem.user_id == callback.from_user.id)
        )
        await session.commit()
    
    await callback.message.edit_text(
        "🛒 <b>Your cart is empty</b>\n\nStart shopping to add items!",
        reply_markup=cart_keyboard(has_items=False)
    )
    await callback.answer("Cart cleared")


async def _display_cart(user_id: int, message: Message):
    """Helper to display cart contents"""
    async with SessionLocal() as session:
        result = await session.execute(
            select(CartItem, Product).join(Product).where(
                CartItem.user_id == user_id
            )
        )
        cart_items = result.all()
    
    if not cart_items:
        await message.answer(
            "🛒 <b>Your cart is empty</b>\n\nStart shopping to add items!",
            reply_markup=cart_keyboard(has_items=False)
        )
        return
    
    text = "🛒 <b>Your Cart:</b>\n\n"
    total = 0
    
    for cart_item, product in cart_items:
        subtotal = product.price * cart_item.quantity
        total += subtotal
        text += (
            f"• <b>{product.name}</b>\n"
            f"  {cart_item.quantity} × {CURRENCY_SYMBOL}{product.price} = "
            f"{CURRENCY_SYMBOL}{subtotal:.2f}\n\n"
        )
    
    text += f"💰 <b>Total: {CURRENCY_SYMBOL}{total:.2f}</b>"
    
    await message.answer(text, reply_markup=cart_keyboard(has_items=True))
