# BPB Telegram Bot

A Telegram bot that automatically deploys [BPB Worker Panel](https://github.com/bia-pain-bache/BPB-Worker-Panel) to Cloudflare Workers with just a few clicks.

## Features

- 🌐 **Multi-language Support** - English and Persian (Farsi)
- 🔒 **Channel Membership Check** - Ensures users join your channel before using the bot
- ⚡ **Automated Deployment** - Deploys BPB Worker Panel to Cloudflare automatically
- 🗄️ **KV Namespace Setup** - Creates and binds KV namespace automatically
- 🔐 **Secret Management** - Generates and sets UUID and TR_PASS automatically
- 📱 **Fragment Subscription** - Provides ready-to-use fragment subscription URLs
- 📚 **Built-in Tutorial** - Step-by-step guide to get Cloudflare API Key

## Requirements

- Python 3.10+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Cloudflare Account

## Deployment on Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

### Step 1: Fork this Repository

Click the "Fork" button at the top right of this page to create your own copy.

### Step 2: Deploy to Railway

1. Go to [Railway](https://railway.app/)
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your forked repository
5. Add the following environment variable:
   - `BOT_TOKEN` - Your Telegram bot token from [@BotFather](https://t.me/botfather)

### Step 3: Start the Bot

Once deployed, Railway will automatically start your bot!

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Your Telegram bot token from BotFather | Yes |

## Usage

1. Start the bot with `/start` command
2. Join the required channel
3. Choose your language (English or Persian)
4. Follow the tutorial to get your Cloudflare API Key
5. Click "Create Worker" button
6. Enter your Cloudflare email
7. Enter your Cloudflare Global API Key
8. Wait for deployment to complete
9. Receive your Panel URL and Fragment Subscription link!

## Getting Cloudflare API Key

1. Sign up or log in to [Cloudflare](https://dash.cloudflare.com/)
2. Go to **My Profile** → **API Tokens**
3. Scroll down to **Global API Key**
4. Click **View** and copy your API Key
5. Use this key in the bot

## Configuration

To change the required channel, edit the `CHANNEL_USERNAME` variable in `main.py`:

```python
CHANNEL_USERNAME = "@your_channel_username"
```

**Note:** Make sure your bot is added as an admin in your channel to check membership.

## Dependencies

- `python-telegram-bot==20.7` - Telegram Bot API wrapper
- `requests==2.31.0` - HTTP library for Cloudflare API calls

## Project Structure

```
BPB-Telegram-bot-main/
├── main.py              # Main bot application
├── requirements.txt     # Python dependencies
├── Procfile            # Railway/Heroku process file
├── runtime.txt         # Python runtime version
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## What Gets Deployed

When you use this bot, it automatically:

1. ✅ Downloads the latest BPB Worker Panel script
2. ✅ Creates a new Cloudflare Worker with a random name
3. ✅ Creates and binds a KV namespace
4. ✅ Generates UUID and Trojan password
5. ✅ Sets up all required secrets
6. ✅ Creates a worker subdomain
7. ✅ Provides you with Panel URL and Fragment subscription link

## Support

For issues and questions:
- Open an issue on this repository
- Check [BPB Worker Panel](https://github.com/bia-pain-bache/BPB-Worker-Panel) documentation

## Credits

- [BPB Worker Panel](https://github.com/bia-pain-bache/BPB-Worker-Panel) - The worker panel that gets deployed
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper

## License

This project is open source and available under the MIT License.

---

Made with ❤️ for easy BPB Worker Panel deployment

