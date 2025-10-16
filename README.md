# Wasabi Storage Bot Premium

A premium Telegram bot for managing cloud storage with Wasabi hot cloud storage integration.

## Features

- 🔐 Secure cloud storage management
- 📁 File upload/download operations
- 🔍 File search and organization
- 👥 Multi-user support with premium tiers
- 💾 Wasabi cloud storage integration
- 🔔 Real-time notifications
- 📊 Storage analytics and usage tracking
- 🔒 End-to-end encryption support
- 🌐 Multi-language support
- ⚡ High-performance file handling

## Installation

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Wasabi Cloud Storage Account
- PostgreSQL/MySQL database (optional)

 ### *Env*
 
 '''bash
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=123456789,987654321

# Wasabi Storage Configuration
WASABI_ACCESS_KEY=your_wasabi_access_key
WASABI_SECRET_KEY=your_wasabi_secret_key
WASABI_ENDPOINT=https://s3.wasabisys.com
WASABI_REGION=us-east-1

# Database Configuration
DATABASE_URL=sqlite:///bot_database.db
# or for PostgreSQL: postgresql://user:password@localhost/dbname

# Security
ENCRYPTION_KEY=your_encryption_key_here
MAX_FILE_SIZE=5368709120  # 5GB in bytes

# Bot Settings
MAX_CONCURRENT_UPLOADS=3
DEFAULT_STORAGE_LIMIT=10737418240  # 10GB
PREMIUM_STORAGE_LIMIT=536870912000  # 500GB

### Quick Setup

1. **Clone the repository**
```bash
git clone https://github.com/Mraprguild/Wasabistoragebotpremium.git
cd Wasabistoragebotpremium
pip install -r requirements.txt
python bot.py

