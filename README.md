
# Redmine Bot Setup Instructions

## 1. Environment Setup

Edit the `.env` file with your credentials:

```env
# Redmine credentials
USERNAME=your_redmine_username
PASSWORD=your_redmine_password

# Telegram bot token (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token

# Your Telegram chat ID (get from @userinfobot)
AUTHORIZED_CHAT_ID=your_chat_id
```

## 2. Getting Telegram Bot Token

1. Message @BotFather on Telegram
2. Use `/newbot` command
3. Follow instructions to create your bot
4. Copy the token to `.env` file

## 3. Getting Your Chat ID

1. Message @userinfobot on Telegram
2. Copy your User ID to `.env` file as AUTHORIZED_CHAT_ID

## 4. Running the Application

### Option 1: Run both services together
```bash
python run_services.py
```

### Option 2: Run separately
Terminal 1 (Flask server):
```bash
python main.py
```

Terminal 2 (Telegram bot):
```bash
python telegram_bot.py
```

## 5. Using the Bot

1. Send `/start` to check server status
2. Send `/form` to begin the automation process
3. Follow the prompts:
   - Enter issue ID
   - Enter notes count (how many times to repeat)
   - Enter note text
4. Bot will process and confirm completion

## 6. Bot Commands

- `/start` - Check server status
- `/form` - Start form automation
- `/cancel` - Cancel current operation  
- `/help` - Show help message

## Troubleshooting

- Make sure your Repl is awake when using the bot
- Verify all credentials in `.env` file
- Check that the Redmine website is accessible
- Ensure Telegram bot token and chat ID are correct
