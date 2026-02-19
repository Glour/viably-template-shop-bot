"""Admin handlers"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, func

from database.db import SessionLocal, Product, Category, Order, OrderItem
from keyboards.admin import admin_menu, order_actions
from config import ADMIN_IDS, CURRENCY_SYMBOL

router = Router()


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Access denied")
        return
    
    await message.answer(
        "🔐 <b>Admin Panel</b>\n\n"
        "Select an option:",
        reply_markup=admin_menu()
    )


@router.message(F.text == "📋 Orders")
async def show_admin_orders(message: Message):
    """Show all orders (admin)"""
    if not is_admin(message.from_user.id):
        return
    
    async with SessionLocal() as session:
        result = await session.execute(
            select(Order).order_by(Order.created_at.desc()).limit(20)
        )
        orders = result.scalars().all()
    
    if not orders:
        await message.answer("📋 No orders yet")
        return
    
    status_emoji = {
        'pending': '⏳',
        'confirmed': '✅',
        'shipped': '🚚',
        'delivered': '✔️',
        'cancelled': '❌'
    }
    
    for order in orders:
        emoji = status_emoji.get(order.status, '❓')
        text = (
            f"{emoji} <b>Order #{order.id}</b>\n"
            f"Customer ID: {order.user_id}\n"
            f"Amount: {CURRENCY_SYMBOL}{order.total_amount:.2f}\n"
            f"Status: {order.status}\n"
            f"Phone: {order.phone}\n"
            f"Address: {order.delivery_address}\n"
            f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
        
        if order.comment:
            text += f"\n💬 Comment: {order.comment}"
        
        await message.answer(text, reply_markup=order_actions(order.id))


@router.callback_query(F.data.startswith("order_"))
async def handle_order_action(callback: CallbackQuery):
    """Handle order status changes"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied", show_alert=True)
        return
    
    action, order_id = callback.data.split("_")[1], int(callback.data.split(":")[1])
    
    status_map = {
        'confirm': 'confirmed',
        'ship': 'shipped',
        'deliver': 'delivered',
        'cancel': 'cancelled'
    }
    
    new_status = status_map.get(action)
    if not new_status:
        return
    
    async with SessionLocal() as session:
        order = await session.get(Order, order_id)
        if order:
            order.status = new_status
            await session.commit()
    
    await callback.answer(f"✅ Order #{order_id} marked as {new_status}")
    
    # Update message
    try:
        text = callback.message.text.split('\n')
        for i, line in enumerate(text):
            if line.startswith('Status:'):
                status_emoji = {'confirmed': '✅', 'shipped': '🚚', 'delivered': '✔️', 'cancelled': '❌'}
                emoji = status_emoji.get(new_status, '❓')
                # Update first line emoji
                text[0] = f"{emoji} <b>Order #{order_id}</b>"
                text[i] = f"Status: {new_status}"
                break
        await callback.message.edit_text('\n'.join(text), reply_markup=order_actions(order_id))
    except:
        pass


@router.message(F.text == "📊 Statistics")
async def show_statistics(message: Message):
    """Show shop statistics"""
    if not is_admin(message.from_user.id):
        return
    
    async with SessionLocal() as session:
        # Total orders
        total_orders = await session.scalar(select(func.count(Order.id)))
        
        # Total revenue
        total_revenue = await session.scalar(select(func.sum(Order.total_amount))) or 0
        
        # Orders by status
        pending = await session.scalar(select(func.count(Order.id)).where(Order.status == 'pending')) or 0
        confirmed = await session.scalar(select(func.count(Order.id)).where(Order.status == 'confirmed')) or 0
        shipped = await session.scalar(select(func.count(Order.id)).where(Order.status == 'shipped')) or 0
        delivered = await session.scalar(select(func.count(Order.id)).where(Order.status == 'delivered')) or 0
        
        # Total products
        total_products = await session.scalar(select(func.count(Product.id)))
        active_products = await session.scalar(select(func.count(Product.id)).where(Product.is_active == True))
    
    text = (
        "📊 <b>Shop Statistics</b>\n\n"
        f"💰 Total Revenue: {CURRENCY_SYMBOL}{total_revenue:.2f}\n"
        f"📦 Total Orders: {total_orders}\n\n"
        f"⏳ Pending: {pending}\n"
        f"✅ Confirmed: {confirmed}\n"
        f"🚚 Shipped: {shipped}\n"
        f"✔️ Delivered: {delivered}\n\n"
        f"📦 Products: {active_products}/{total_products} active"
    )
    
    await message.answer(text)


@router.message(F.text == "◀️ Back to shop")
async def back_to_shop(message: Message):
    """Return to user mode"""
    from keyboards.user import main_menu
    await message.answer("👤 User mode", reply_markup=main_menu())
