# 🚀 Wasabi Storage Bot Premium

A **premium Telegram bot** for managing cloud storage with **Wasabi Hot Cloud Storage integration**.  
Easily upload, download, and manage files with speed, security, and reliability.

---

## 🌟 Features

- 🔐 **Secure Cloud Storage Management**
- 📁 **File Upload & Download Operations**
- 🔍 **File Search and Organization**
- 👥 **Multi-User Support with Premium Tiers**
- 💾 **Wasabi Cloud Integration**
- 🔔 **Real-Time Notifications**
- 📊 **Storage Analytics and Usage Tracking**
- 🔒 **End-to-End Encryption Support**
- 🌐 **Multi-Language Support**
- ⚡ **High-Performance File Handling**

---

## 🧩 Installation

### Prerequisites

- Python **3.8+**
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Wasabi Cloud Storage Account
- PostgreSQL/MySQL database *(optional)*

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory and add the following:

```bash
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
MAX_FILE_SIZE=5368709120  # 5GB

# Bot Settings
MAX_CONCURRENT_UPLOADS=3
DEFAULT_STORAGE_LIMIT=10737418240   # 10GB
PREMIUM_STORAGE_LIMIT=536870912000  # 500GB


### Quick Setup

1. **Clone the repository**
```bash
git clone https://github.com/Mraprguild/Wasabistoragebotpremium.git
cd Wasabistoragebotpremium
pip install -r requirements.txt
python bot.py

