import os
import asyncio
import time
import math
import json
from datetime import datetime
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from pyrogram.enums import ParseMode

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

from config import config

# Initialize download directory
if not os.path.exists(config.DOWNLOAD_DIR):
    os.makedirs(config.DOWNLOAD_DIR)

# Global variables
drive_service = None
app = None

# --- Google Drive Authentication ---
def get_gdrive_service():
    """Initialize Google Drive service with improved error handling"""
    global drive_service
    
    creds = None
    try:
        # Load existing token
        if os.path.exists(config.GDRIVE_TOKEN_JSON):
            creds = Credentials.from_authorized_user_file(config.GDRIVE_TOKEN_JSON, config.SCOPES)
        
        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Handle credentials from file or environment variable
                if os.path.exists(config.GDRIVE_CREDENTIALS_JSON):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        config.GDRIVE_CREDENTIALS_JSON, config.SCOPES
                    )
                else:
                    # Try to parse from environment variable
                    try:
                        creds_data = json.loads(config.GDRIVE_CREDENTIALS_JSON)
                        flow = InstalledAppFlow.from_client_config(creds_data, config.SCOPES)
                    except (json.JSONDecodeError, ValueError):
                        raise ValueError("Invalid GDRIVE_CREDENTIALS_JSON format")
                
                print("🔐 Google Drive Authorization Required")
                print("Please visit the following URL to authorize the application:")
                auth_url, _ = flow.authorization_url(prompt='consent')
                print(f"\n{auth_url}\n")
                
                code = input("Enter the authorization code: ").strip()
                flow.fetch_token(code=code)
                creds = flow.credentials
                
                # Save token for future use
                with open(config.GDRIVE_TOKEN_JSON, 'w') as token:
                    token.write(creds.to_json())
                print("✅ Authorization successful! Token saved.")
        
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Test the connection
        drive_service.about().get(fields="user").execute()
        print("✅ Google Drive service initialized successfully")
        return drive_service
        
    except Exception as e:
        print(f"❌ Failed to initialize Google Drive: {e}")
        return None

# --- Utility Functions ---
def humanbytes(size: int) -> str:
    """Convert bytes to human readable format"""
    if not size or size == 0:
        return "0 B"
    
    power = 1024
    power_labels = ["B", "KB", "MB", "GB", "TB"]
    power_index = 0
    
    while size > power and power_index < len(power_labels) - 1:
        size /= power
        power_index += 1
    
    return f"{size:.2f} {power_labels[power_index]}"

def escape_markdown(text: str) -> str:
    """Escape special characters for markdownv2"""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

async def progress_callback(current: int, total: int, message: Message, start_time: float, action: str):
    """Update progress message"""
    now = time.time()
    diff = now - start_time
    
    # Update every 5 seconds or when completed
    if round(diff % 5.00) == 0 or current == total:
        try:
            percentage = (current / total) * 100
            speed = current / diff if diff > 0 else 0
            elapsed_time = round(diff)
            eta = round((total - current) / speed) if speed > 0 else 0
            
            # Progress bar
            filled_blocks = math.floor(percentage / 10)
            empty_blocks = 10 - filled_blocks
            progress_bar = "[" + "█" * filled_blocks + "░" * empty_blocks + "]"
            
            progress_text = (
                f"**{action}**\n\n"
                f"{progress_bar} **{percentage:.1f}%**\n"
                f"**Size:** {humanbytes(total)}\n"
                f"**Done:** {humanbytes(current)}\n"
                f"**Speed:** {humanbytes(speed)}/s\n"
                f"**ETA:** {time.strftime('%H:%M:%S', time.gmtime(eta))}\n"
                f"**Elapsed:** {time.strftime('%H:%M:%S', time.gmtime(elapsed_time))}"
            )
            
            await message.edit_text(progress_text)
            
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except Exception as e:
            print(f"Progress update error: {e}")

# --- Google Drive Operations ---
async def upload_to_drive(file_path: str, message: Message, start_time: float) -> Optional[dict]:
    """Upload file to Google Drive with progress tracking"""
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_path, resumable=True)
        
        # Create upload request
        request = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink, mimeType, size'
        )
        
        # Execute upload with progress
        response = None
        last_update = time.time()
        
        while response is None:
            status, response = request.next_chunk()
            if status:
                current_progress = status.resumable_progress
                current_time = time.time()
                
                # Update progress every 3 seconds to avoid spam
                if current_time - last_update >= 3:
                    await progress_callback(
                        current_progress, 
                        file_size, 
                        message, 
                        start_time, 
                        "📤 Uploading to Google Drive"
                    )
                    last_update = current_time
        
        # Make file publicly accessible
        drive_service.permissions().create(
            fileId=response['id'],
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        return response
        
    except HttpError as e:
        await message.edit_text(f"❌ Google Drive API Error: {e}")
    except Exception as e:
        await message.edit_text(f"❌ Upload failed: {e}")
    
    return None

# --- Bot Handlers (will be registered after app initialization) ---
def register_handlers():
    """Register all bot handlers"""
    
    @app.on_message(filters.command("start"))
    async def start_handler(client, message: Message):
        """Handle /start command"""
        welcome_text = """
🤖 **Google Drive Bot**

I can help you upload files to Google Drive and download files from Google Drive links.

**Commands:**
/start - Show this message
/help - Get detailed help
/status - Check bot status

**How to use:**
• Send me any file to upload to Google Drive
• Send a Google Drive link to download it here

**Privacy:** Your files are only stored temporarily during transfer.
        """
        
        await message.reply_text(welcome_text)

    @app.on_message(filters.command("help"))
    async def help_handler(client, message: Message):
        """Handle /help command"""
        help_text = """
📖 **How to use this bot:**

**Upload to Google Drive:**
Simply send me any file (document, video, audio, photo) and I'll upload it to Google Drive.

**Download from Google Drive:**
Send me a Google Drive file link and I'll download it for you.

**Supported file types:**
• Documents (PDF, DOC, TXT, etc.)
• Videos (MP4, AVI, MKV, etc.)
• Audio files (MP3, WAV, etc.)
• Images (JPG, PNG, etc.)
• Archives (ZIP, RAR, etc.)

**File size limits:**
• Telegram limit: 2GB
• Google Drive limit: 5TB

**Note:** Large files may take longer to process.
        """
        
        await message.reply_text(help_text)

    @app.on_message(filters.command("status"))
    async def status_handler(client, message: Message):
        """Handle /status command"""
        gdrive_status = "✅ Connected" if drive_service else "❌ Disconnected"
        download_dir_status = "✅ Exists" if os.path.exists(config.DOWNLOAD_DIR) else "❌ Missing"
        owner_id = config.OWNER_ID or 'Not set'
        
        status_text = f"""
🤖 **Bot Status**

**Google Drive:** {gdrive_status}
**Download Directory:** {download_dir_status}
**Owner ID:** `{owner_id}`
        """
        
        await message.reply_text(status_text)

    @app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
    async def handle_file_upload(client, message: Message):
        """Handle file uploads from Telegram to Google Drive"""
        if not drive_service:
            await message.reply_text("❌ Google Drive service is not available. Please contact the bot owner.")
            return
        
        file_path = None
        try:
            start_time = time.time()
            
            # Initial status message
            status_message = await message.reply_text("📥 **Downloading file...**", quote=True)
            
            # Download file from Telegram
            file_path = await message.download(
                file_name=config.DOWNLOAD_DIR,
                progress=progress_callback,
                progress_args=(status_message, start_time, "📥 Downloading from Telegram")
            )
            
            if not file_path:
                await status_message.edit_text("❌ Failed to download file")
                return
            
            await status_message.edit_text("✅ Download complete! Starting upload to Google Drive...")
            
            # Upload to Google Drive
            result = await upload_to_drive(file_path, status_message, start_time)
            
            if result:
                file_link = result.get('webViewLink', 'N/A')
                file_name = result.get('name', 'Unknown')
                file_size = humanbytes(int(result.get('size', 0)))
                
                success_text = f"""
✅ **File Uploaded Successfully!**

**File Name:** `{file_name}`
**File Size:** `{file_size}`
**Google Drive Link:** [Click Here]({file_link})
                """
                
                await status_message.edit_text(
                    success_text,
                    disable_web_page_preview=True
                )
            else:
                await status_message.edit_text("❌ Failed to upload file to Google Drive")
                
        except Exception as e:
            error_msg = f"❌ An error occurred: {str(e)}"
            try:
                await message.reply_text(error_msg)
            except:
                pass
        finally:
            # Clean up downloaded file
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass

    @app.on_message(filters.private & filters.text)
    async def handle_text_messages(client, message: Message):
        """Handle text messages (potential Google Drive links)"""
        text = message.text.strip()
        
        # Basic Google Drive link detection
        if 'drive.google.com' in text:
            await message.reply_text(
                "🔗 **Google Drive Link Detected**\n\n"
                "Download from Google Drive feature is coming soon!\n"
                "For now, I can only upload files to Google Drive."
            )
        else:
            await message.reply_text(
                "🤖 Send me a file to upload to Google Drive, or use /help for more information."
            )

# --- Application Lifecycle ---
async def initialize_app():
    """Initialize the application"""
    global app, drive_service
    
    try:
        # Validate configuration
        config.validate()
        
        # Initialize Google Drive service
        print("🔄 Initializing Google Drive service...")
        drive_service = get_gdrive_service()
        
        # Initialize Telegram client
        print("🔄 Initializing Telegram client...")
        app = Client(
            "gdrive_bot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

async def main():
    """Main application entry point"""
    if not await initialize_app():
        print("❌ Failed to initialize application. Exiting.")
        return
    
    print("✅ Bot is starting...")
    
    try:
        # Register handlers after app is initialized
        register_handlers()
        
        await app.start()
        print("✅ Bot started successfully!")
        
        # Get bot info
        bot = await app.get_me()
        print(f"🤖 Bot: @{bot.username} (ID: {bot.id})")
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except Exception as e:
        print(f"❌ Bot runtime error: {e}")
    finally:
        print("🛑 Bot is stopping...")
        await app.stop()
        print("✅ Bot stopped successfully")

if __name__ == "__main__":
    # Create event loop and run
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        loop.close()
