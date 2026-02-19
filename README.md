# 🛍 Shop Bot - Telegram E-commerce Bot

A complete Telegram shop bot built with **aiogram 3.x** and **SQLAlchemy**. Ready to deploy and start selling!

## ✨ Features

- 📁 **Product Categories** - Organize products into categories
- 🛒 **Shopping Cart** - Add/remove items, view cart
- 💳 **Checkout** - Complete order with delivery info
- 📦 **Order Management** - Track order status
- 🔐 **Admin Panel** - Manage products, orders, and view statistics
- 💾 **Database** - SQLite (dev) / PostgreSQL (prod)

## 🚀 Quick Start

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/magnetapp/viably-template-shop-bot.git
cd viably-template-shop-bot
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your BOT_TOKEN and ADMIN_IDS
```

4. **Run the bot:**
```bash
python bot.py
```

## 📦 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | Telegram Bot Token from [@BotFather](https://t.me/BotFather) |
| `ADMIN_IDS` | ✅ | Comma-separated admin user IDs |
| `DATABASE_URL` | ⚠️ | Database URL (default: `sqlite:///shop.db`) |
| `SHOP_NAME` | ❌ | Your shop name (default: "My Shop") |
| `CURRENCY` | ❌ | Currency code (default: "USD") |
| `CURRENCY_SYMBOL` | ❌ | Currency symbol (default: "$") |
| `SUPPORT_CONTACT` | ❌ | Support contact (default: "@support") |
| `ORDER_NOTIFICATION_CHAT` | ❌ | Chat ID for order notifications |

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Manual Docker Build

```bash
docker build -t shop-bot .
docker run -d --env-file .env shop-bot
```

## ☁️ Cloud Deployment

### Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

1. Click the button above
2. Connect your GitHub repository
3. Add environment variables
4. Deploy!

### Render

1. Create new **Web Service**
2. Connect repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python bot.py`
5. Add environment variables

### VPS (Ubuntu/Debian)

```bash
# Use the deploy script
chmod +x deploy.sh
./deploy.sh
```

## 🔧 Configuration

### Database

**Development (SQLite):**
```env
DATABASE_URL=sqlite:///shop.db
```

**Production (PostgreSQL):**
```env
DATABASE_URL=postgresql://user:password@host:5432/database
```

### Adding Initial Products

Use the `/admin` command in Telegram to access the admin panel, or add products directly to the database:

```python
# Example: Add products via Python
from database.db import SessionLocal, Product, Category
import asyncio

async def add_sample_products():
    async with SessionLocal() as session:
        category = Category(name="Electronics", emoji="📱")
        session.add(category)
        await session.flush()
        
        product = Product(
            category_id=category.id,
            name="iPhone 15 Pro",
            description="Latest Apple smartphone",
            price=999.99,
            stock=10,
            image_url="https://example.com/iphone.jpg"
        )
        session.add(product)
        await session.commit()

asyncio.run(add_sample_products())
```

## 📱 Bot Commands

### User Commands
- `/start` - Start the bot
- Main menu: Catalog, Cart, Orders, Info

### Admin Commands
- `/admin` - Open admin panel
- Manage products, categories, orders
- View statistics

## 🛠 Project Structure

```
shop-bot/
├── bot.py              # Main bot entry point
├── config.py           # Configuration
├── requirements.txt    # Dependencies
├── .env.example        # Environment template
├── Dockerfile          # Docker image
├── docker-compose.yml  # Docker Compose config
├── deploy.sh           # Deployment script
├── database/
│   └── db.py          # Database models
├── handlers/
│   ├── user.py        # User handlers
│   ├── cart.py        # Cart handlers
│   ├── checkout.py    # Checkout flow
│   └── admin.py       # Admin panel
└── keyboards/
    ├── user.py        # User keyboards
    └── admin.py       # Admin keyboards
```

## 🔒 Security

- Never commit `.env` file
- Keep `BOT_TOKEN` secret
- Use strong database passwords in production
- Restrict admin access via `ADMIN_IDS`

## 📄 License

MIT License - feel free to use for commercial projects!

## 🤝 Support

Created with ❤️ by [Viably](https://github.com/magnetapp/viably)

Need help? Open an issue or contact support!

---

**Made with Viably Template Generator** 🎨
