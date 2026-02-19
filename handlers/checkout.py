"""Checkout and order handlers"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, delete

from database.db import SessionLocal, CartItem, Product, Order, OrderItem
from keyboards.user import confirm_order_keyboard
from config import CURRENCY_SYMBOL, ORDER_NOTIFICATION_CHAT

router = Router()


class CheckoutStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_comment = State()


@router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    """Start checkout process"""
    async with SessionLocal() as session:
        result = await session.execute(
            select(CartItem).where(CartItem.user_id == callback.from_user.id)
        )
        if not result.scalars().first():
            await callback.answer("Your cart is empty!", show_alert=True)
            return
    
    await callback.message.edit_text(
        "📦 <b>Checkout</b>\n\n"
        "Please enter your phone number:"
    )
    await state.set_state(CheckoutStates.waiting_for_phone)
    await callback.answer()


@router.message(CheckoutStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Process phone number"""
    await state.update_data(phone=message.text)
    await message.answer(
        "📍 Please enter your delivery address:"
    )
    await state.set_state(CheckoutStates.waiting_for_address)


@router.message(CheckoutStates.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    """Process delivery address"""
    await state.update_data(address=message.text)
    await message.answer(
        "💬 Any comments or special requests? (or send /skip)"
    )
    await state.set_state(CheckoutStates.waiting_for_comment)


@router.message(CheckoutStates.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    """Process comment and show order confirmation"""
    comment = None if message.text == "/skip" else message.text
    await state.update_data(comment=comment)
    
    # Get order data
    data = await state.get_data()
    
    # Get cart items
    async with SessionLocal() as session:
        result = await session.execute(
            select(CartItem, Product).join(Product).where(
                CartItem.user_id == message.from_user.id
            )
        )
        cart_items = result.all()
    
    if not cart_items:
        await message.answer("❌ Your cart is empty!")
        await state.clear()
        return
    
    # Build order summary
    text = "📋 <b>Order Confirmation</b>\n\n"
    total = 0
    
    for cart_item, product in cart_items:
        subtotal = product.price * cart_item.quantity
        total += subtotal
        text += f"• {product.name} × {cart_item.quantity} = {CURRENCY_SYMBOL}{subtotal:.2f}\n"
    
    text += (
        f"\n💰 <b>Total: {CURRENCY_SYMBOL}{total:.2f}</b>\n\n"
        f"📞 Phone: {data['phone']}\n"
        f"📍 Address: {data['address']}\n"
    )
    
    if data.get('comment'):
        text += f"💬 Comment: {data['comment']}\n"
    
    text += "\n✅ Confirm your order?"
    
    await state.update_data(total=total)
    await message.answer(text, reply_markup=confirm_order_keyboard())


@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    """Confirm and create order"""
    data = await state.get_data()
    
    async with SessionLocal() as session:
        # Get cart items
        result = await session.execute(
            select(CartItem, Product).join(Product).where(
                CartItem.user_id == callback.from_user.id
            )
        )
        cart_items = result.all()
        
        if not cart_items:
            await callback.answer("Cart is empty!", show_alert=True)
            return
        
        # Create order
        order = Order(
            user_id=callback.from_user.id,
            total_amount=data['total'],
            delivery_address=data['address'],
            phone=data['phone'],
            comment=data.get('comment'),
            status='pending'
        )
        session.add(order)
        await session.flush()
        
        # Create order items
        for cart_item, product in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_name=product.name,
                quantity=cart_item.quantity,
                price=product.price
            )
            session.add(order_item)
        
        # Clear cart
        await session.execute(
            delete(CartItem).where(CartItem.user_id == callback.from_user.id)
        )
        
        await session.commit()
        order_id = order.id
    
    await callback.message.edit_text(
        f"✅ <b>Order #{order_id} created!</b>\n\n"
        "Thank you for your purchase!\n"
        "We'll contact you soon to confirm delivery.\n\n"
        f"💰 Total: {CURRENCY_SYMBOL}{data['total']:.2f}"
    )
    
    # Notify admin if configured
    if ORDER_NOTIFICATION_CHAT:
        try:
            from aiogram import Bot
            bot: Bot = callback.bot
            await bot.send_message(
                ORDER_NOTIFICATION_CHAT,
                f"🔔 <b>New Order #{order_id}</b>\n\n"
                f"Customer: {callback.from_user.full_name}\n"
                f"Total: {CURRENCY_SYMBOL}{data['total']:.2f}\n"
                f"Phone: {data['phone']}"
            )
        except:
            pass
    
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """Cancel checkout"""
    await state.clear()
    await callback.message.edit_text("❌ Order cancelled")
    await callback.answer()


@router.message(F.text == "📦 My Orders")
async def show_orders(message: Message):
    """Show user's orders"""
    async with SessionLocal() as session:
        result = await session.execute(
            select(Order).where(Order.user_id == message.from_user.id).order_by(Order.created_at.desc()).limit(10)
        )
        orders = result.scalars().all()
    
    if not orders:
        await message.answer("📦 You have no orders yet")
        return
    
    text = "📦 <b>Your Orders:</b>\n\n"
    
    status_emoji = {
        'pending': '⏳',
        'confirmed': '✅',
        'shipped': '🚚',
        'delivered': '✔️',
        'cancelled': '❌'
    }
    
    for order in orders:
        emoji = status_emoji.get(order.status, '❓')
        text += (
            f"{emoji} <b>Order #{order.id}</b>\n"
            f"Amount: {CURRENCY_SYMBOL}{order.total_amount:.2f}\n"
            f"Status: {order.status}\n"
            f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        )
    
    await message.answer(text)
