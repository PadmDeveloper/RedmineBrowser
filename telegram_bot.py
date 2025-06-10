
import os
import asyncio
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
import logging

# Load environment variables (Replit secrets take precedence)
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

# Bot token and authorized chat ID (prioritize Replit environment)
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
AUTHORIZED_CHAT_ID = os.environ.get('AUTHORIZED_CHAT_ID') or os.getenv('AUTHORIZED_CHAT_ID')
FLASK_SERVER_URL = "http://localhost:5000"  # Change to your actual server URL when deployed

# Convert AUTHORIZED_CHAT_ID to int if it exists
if AUTHORIZED_CHAT_ID:
    try:
        AUTHORIZED_CHAT_ID = int(AUTHORIZED_CHAT_ID)
    except ValueError:
        print("Error: AUTHORIZED_CHAT_ID must be a valid integer")
        AUTHORIZED_CHAT_ID = None

# Conversation states
WAITING_FOR_ID, WAITING_FOR_NOTES_COUNT, WAITING_FOR_NOTE = range(3)

# Store conversation data
user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    if not update.message:
        logging.error("Received update with no message.")
        return
        
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        logging.error("Received update with no chat information.")
        return

    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access")
        return

    try:
        # Check if Flask server is running
        response = requests.get(f"{FLASK_SERVER_URL}/", timeout=5)
        if response.status_code == 200:
            await update.message.reply_text("✅ Server is active")
        else:
            await update.message.reply_text("❌ Server error")
    except requests.exceptions.RequestException:
        await update.message.reply_text("❌ Server is not responding")


async def form_command(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /form command"""
    if not update.message:
        logging.error("Received update with no message.")
        return ConversationHandler.END
        
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        logging.error("Received update with no chat information.")
        return ConversationHandler.END

    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access")
        return ConversationHandler.END

    await update.message.reply_text("📝 Please enter the issue ID:")
    return WAITING_FOR_ID


async def get_issue_id(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get issue ID from user"""
    if not update.message or not update.message.text:
        return WAITING_FOR_ID
        
    issue_id = update.message.text.strip()

    # Validate issue ID (should be numeric)
    if not issue_id.isdigit():
        await update.message.reply_text(
            "❌ Invalid ID. Please enter a numeric issue ID:")
        return WAITING_FOR_ID

    user_data['issue_id'] = issue_id
    await update.message.reply_text("🔢 Please enter the notes count:")
    return WAITING_FOR_NOTES_COUNT


async def get_notes_count(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get notes count from user"""
    if not update.message or not update.message.text:
        return WAITING_FOR_NOTES_COUNT
        
    notes_count = update.message.text.strip()

    # Validate notes count (should be numeric and positive)
    if not notes_count.isdigit() or int(notes_count) <= 0:
        await update.message.reply_text(
            "❌ Invalid count. Please enter a positive number:")
        return WAITING_FOR_NOTES_COUNT

    user_data['notes_count'] = int(notes_count)
    await update.message.reply_text("📝 Please enter the note text:")
    return WAITING_FOR_NOTE


async def get_note_text(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get note text and process the request"""
    if not update.message or not update.message.text:
        return WAITING_FOR_NOTE
        
    note_text = update.message.text.strip()

    if not note_text:
        await update.message.reply_text(
            "❌ Note text cannot be empty. Please enter the note:")
        return WAITING_FOR_NOTE

    user_data['note_text'] = note_text

    # Show processing message
    await update.message.reply_text(
        "⏳ Processing your request... This may take a moment.")

    try:
        # Send request to Flask server
        payload = {
            'issue_id': user_data['issue_id'],
            'notes_count': user_data['notes_count'],
            'note_text': user_data['note_text']
        }

        response = requests.post(f"{FLASK_SERVER_URL}/add_note",
                                 json=payload,
                                 timeout=60)

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                await update.message.reply_text(
                    f"✅ Note successfully added to issue {user_data['issue_id']}"
                )
            else:
                await update.message.reply_text(
                    f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            await update.message.reply_text("❌ Server error occurred")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Connection error: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"❌ Unexpected error: {str(e)}")

    # Clear user data
    user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    if not update.message:
        return ConversationHandler.END
        
    await update.message.reply_text("❌ Operation cancelled")
    user_data.clear()
    return ConversationHandler.END


async def help_command(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message"""
    if not update.message:
        logging.error("Received update with no message.")
        return
        
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        logging.error("Received update with no chat information.")
        return

    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access")
        return

    help_text = """
🤖 **Redmine Bot Commands:**

/start - Check server status
/form - Start form filling process
/cancel - Cancel current operation
/help - Show this help message

**Process:**
1. Use /form to start
2. Enter issue ID
3. Enter notes count
4. Enter note text
5. Bot will process and confirm
    """
    await update.message.reply_text(help_text)


def main():
    """Start the bot"""
    if not BOT_TOKEN or BOT_TOKEN == 'your_telegram_bot_token_here':
        print("Error: TELEGRAM_BOT_TOKEN not found or not set properly in environment variables")
        print("Please check your .env file or Replit Secrets")
        return

    if not AUTHORIZED_CHAT_ID:
        print("Error: AUTHORIZED_CHAT_ID not found or not set properly in environment variables")
        print("Please check your .env file or Replit Secrets")
        return

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('form', form_command)],
        states={
            WAITING_FOR_ID:
            [MessageHandler(filters.TEXT & ~filters.COMMAND, get_issue_id)],
            WAITING_FOR_NOTES_COUNT:
            [MessageHandler(filters.TEXT & ~filters.COMMAND, get_notes_count)],
            WAITING_FOR_NOTE:
            [MessageHandler(filters.TEXT & ~filters.COMMAND, get_note_text)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)

    # Run the bot
    print("🤖 Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
