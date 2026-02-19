"""User handlers"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from database.db import SessionLocal, User, Category, Product
from keyboards.user import main_menu, categories_keyboard, products_keyboard, product_detail_keyboard
from config import SHOP_NAME

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Start command handler"""
    async with SessionLocal() as session:
        # Add user to database
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(
                id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )
            session.add(user)
            await session.commit()
    
    await message.answer(
        f"👋 Welcome to <b>{SHOP_NAME}</b>!\n\n"
        "🛍 Browse our catalog and add items to your cart\n"
        "🛒 View your cart and checkout anytime\n"
        "📦 Track your orders\n\n"
        "Use the menu below to get started:",
        reply_markup=main_menu()
    )


@router.message(F.text == "🛍 Catalog")
@router.callback_query(F.data == "categories")
async def show_categories(event: Message | CallbackQuery):
    """Show categories"""
    async with SessionLocal() as session:
        result = await session.execute(
            select(Category).where(Category.is_active == True)
        )
        categories = result.scalars().all()
    
    text = "📁 <b>Choose a category:</b>"
    keyboard = categories_keyboard(categories)
    
    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard)
    else:
        await event.message.edit_text(text, reply_markup=keyboard)
        await event.answer()


@router.callback_query(F.data.startswith("category:"))
async def show_products(callback: CallbackQuery):
    """Show products in category"""
    category_id = int(callback.data.split(":")[1])
    
    async with SessionLocal() as session:
        category = await session.get(Category, category_id)
        result = await session.execute(
            select(Product).where(
                Product.category_id == category_id,
                Product.is_active == True
            )
        )
        products = result.scalars().all()
    
    if not products:
        await callback.answer("This category is empty", show_alert=True)
        return
    
    text = f"{category.emoji} <b>{category.name}</b>\n\n{category.description or ''}\n\nSelect a product:"
    keyboard = products_keyboard(products, category_id)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("product:"))
async def show_product(callback: CallbackQuery):
    """Show product details"""
    product_id = int(callback.data.split(":")[1])
    
    async with SessionLocal() as session:
        product = await session.get(Product, product_id)
        if not product:
            await callback.answer("Product not found", show_alert=True)
            return
        
        # Check if in cart
        from database.db import CartItem
        result = await session.execute(
            select(CartItem).where(
                CartItem.user_id == callback.from_user.id,
                CartItem.product_id == product_id
            )
        )
        in_cart = result.scalar_one_or_none() is not None
    
    text = (
        f"<b>{product.name}</b>\n\n"
        f"{product.description}\n\n"
        f"💰 Price: <b>${product.price}</b>\n"
        f"📦 In stock: {product.stock} pcs"
    )
    
    if product.image_url:
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=product.image_url,
            caption=text,
            reply_markup=product_detail_keyboard(product_id, in_cart)
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=product_detail_keyboard(product_id, in_cart)
        )
    
    await callback.answer()


@router.message(F.text == "ℹ️ Info")
async def show_info(message: Message):
    """Show shop info"""
    from config import SUPPORT_CONTACT
    await message.answer(
        f"ℹ️ <b>About {SHOP_NAME}</b>\n\n"
        "This is a demo shop bot created with Viably template.\n\n"
        f"📞 Support: {SUPPORT_CONTACT}\n"
        "⏰ Working hours: 24/7\n"
        "🚚 Delivery: Worldwide"
    )
