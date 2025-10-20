import os
import asyncio
import uuid
import secrets
import string
import requests
import re
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from telegram.error import TelegramError

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@svdplaylist"

# Worker script source URL
WORKER_JS_URL = "https://github.com/bia-pain-bache/BPB-Worker-Panel/releases/download/v3.6.1/worker.js"

CHOOSE_LANGUAGE, ASK_EMAIL, ASK_API_KEY = range(3)

user_data = {}

MESSAGES = {
    "en": {
        "welcome": "Welcome to BPB Worker Panel Bot!\n\n⚠️ You must join our channel to use this bot.",
        "join_button": "Join Channel",
        "check_button": "I Joined ✅",
        "not_joined": "❌ You haven't joined the channel yet!\nPlease join first, then click 'I Joined ✅'",
        "choose_language": "Please choose your language:\nلطفا زبان خود را انتخاب کنید:",
        "language_set": "✅ Language set to English",
        "tutorial": "📚 Tutorial - How to get Cloudflare API Key:\n\n"
                   "1. If you don't have a Cloudflare account, click 'Sign Up' to create one\n"
                   "2. If you already have an account, click 'Sign In' to login\n"
                   "3. After logging in, click 'Get API Key' to go directly to your API Tokens page\n\n"
                   "📝 Steps to get your API Key:\n"
                   "- Scroll down to 'Global API Key'\n"
                   "- Click 'View' button\n"
                   "- Copy your Global API Key\n\n"
                   "When ready, click 'Create Worker' button!",
        "signup_button": "Sign Up to Cloudflare",
        "signin_button": "Sign In to Cloudflare",
        "apikey_button": "Get API Key",
        "create_button": "Create Worker ⚡",
        "ask_email": "Please enter your Cloudflare email address:",
        "ask_api": "Please enter your Cloudflare Global API Key:",
        "deploying": "🚀 Starting deployment...\nThis may take a few minutes.",
        "account_info": "📋 Getting account information...",
        "downloading": "📥 Downloading worker script...",
        "creating_kv": "🗄️ Creating kv namespace...",
        "uploading": "☁️ Uploading worker to Cloudflare...",
        "secrets": "🔧 Setting up variables...",
        "subdomain": "🌐 Creating worker subdomain...",
        "success": "✅ Deployment completed successfully!\n\n🔗 Panel URL: {}\n📲 Fragment Subscription: `{}`\n\nUse the fragment subscription URL in your V2Ray client!\n\nPlease wait about 5 to 10 minutes for the panel to be created.\nIn V2Ray, Mahsang, Streisand, or V2Box, add the subscription, tap 'Update subscription', and connect to 'Best fragment'.\nIf it didn't work, open the panel link, go to 'Vless - Trojan', enable all ports for both 'TLS port' and 'Non-TLS port', click 'Apply', then tap 'Update subscription' again.",
        "error": "❌ Error: {}"
    },
    "fa": {
        "welcome": "به ربات BPB Worker Panel خوش آمدید!\n\n⚠️ برای استفاده از این ربات باید در کانال ما عضو شوید.",
        "join_button": "عضویت در کانال",
        "check_button": "عضو شدم ✅",
        "not_joined": "❌ شما هنوز در کانال عضو نشده‌اید!\nلطفا ابتدا عضو شوید، سپس روی 'عضو شدم ✅' کلیک کنید",
        "choose_language": "Please choose your language:\nلطفا زبان خود را انتخاب کنید:",
        "language_set": "✅ زبان به فارسی تنظیم شد",
        "tutorial": "📚 آموزش - نحوه دریافت API Key کلودفلر:\n\n"
                   "۱. اگر اکانت کلودفلر ندارید، روی 'ثبت نام' کلیک کنید\n"
                   "۲. اگر قبلا اکانت دارید، روی 'ورود' کلیک کنید\n"
                   "۳. بعد از ورود، روی 'دریافت API Key' کلیک کنید تا مستقیم به صفحه API Tokens بروید\n\n"
                   "📝 مراحل دریافت API Key:\n"
                   "- به پایین اسکرول کنید تا 'Global API Key' را پیدا کنید\n"
                   "- روی دکمه 'View' کلیک کنید\n"
                   "- Global API Key خود را کپی کنید\n\n"
                   "وقتی آماده شدید، روی دکمه 'ساخت Worker' کلیک کنید!",
        "signup_button": "ثبت نام در کلودفلر",
        "signin_button": "ورود به کلودفلر",
        "apikey_button": "دریافت API Key",
        "create_button": "ساخت Worker ⚡",
        "ask_email": "لطفا ایمیل کلودفلر خود را وارد کنید:",
        "ask_api": "لطفا Global API Key کلودفلر خود را وارد کنید:",
        "deploying": "🚀 شروع نصب...\nاین کار ممکن است چند دقیقه طول بکشد.",
        "account_info": "📋 دریافت اطلاعات اکانت...",
        "downloading": "📥 دانلود اسکریپت worker...",
        "creating_kv": "🗄️ ساخت kv namespace...",
        "uploading": "☁️ آپلود worker به کلودفلر...",
        "secrets": "🔧 در حال تنظیم متغیرها...",
        "subdomain": "🌐 ساخت subdomain برای worker...",
        "success": "✅ نصب با موفقیت انجام شد!\n\n🔗 آدرس پنل: {}\n📲 لینک اشتراک Fragment: `{}`\n\nلینک اشتراک را در کلاینت V2Ray خود استفاده کنید!\n\nحدود 5 تا 10 دقیقه منتظر بمانید تا پنل ساخته شود.\nدر نرم‌افزارهای V2Ray، Mahsang، Streisand یا V2Box، اشتراک را اضافه کنید، گزینه 'Update subscription' را بزنید و به گزینه 'Best fragment' وصل شوید.\nاگر نشد، وارد لینک پنل شوید، به بخش 'Vless - Trojan' بروید، جلوی 'TLS port' و 'Non-TLS port' تیک همه پورت‌ها را بزنید و 'Apply' کنید، سپس دوباره 'Update subscription' را بزنید.",
        "error": "❌ خطا: {}"
    }
}

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await check_membership(update, context):
        keyboard = [
            [InlineKeyboardButton("Join Channel", url="https://t.me/svdplaylist")],
            [InlineKeyboardButton("I Joined ✅", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Welcome to BPB Worker Panel Bot!\n\n⚠️ You must join our channel to use this bot.",
            reply_markup=reply_markup
        )
        return CHOOSE_LANGUAGE
    
    keyboard = [
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton("فارسی 🇮🇷", callback_data="lang_fa")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please choose your language:\nلطفا زبان خود را انتخاب کنید:",
        reply_markup=reply_markup
    )
    return CHOOSE_LANGUAGE

async def check_membership_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not await check_membership(update, context):
        await query.edit_message_text(
            "❌ You haven't joined the channel yet!\nPlease join first, then click 'I Joined ✅'"
        )
        keyboard = [
            [InlineKeyboardButton("Join Channel", url="https://t.me/svdplaylist")],
            [InlineKeyboardButton("I Joined ✅", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "Welcome to BPB Worker Panel Bot!\n\n⚠️ You must join our channel to use this bot.",
            reply_markup=reply_markup
        )
        return CHOOSE_LANGUAGE
    
    keyboard = [
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton("فارسی 🇮🇷", callback_data="lang_fa")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "Please choose your language:\nلطفا زبان خود را انتخاب کنید:",
        reply_markup=reply_markup
    )
    return CHOOSE_LANGUAGE

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = query.data.split("_")[1]
    
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["language"] = lang
    
    msg = MESSAGES[lang]
    
    keyboard = [
        [InlineKeyboardButton(msg["signup_button"], url="https://dash.cloudflare.com/sign-up")],
        [InlineKeyboardButton(msg["signin_button"], url="https://dash.cloudflare.com/login")],
        [InlineKeyboardButton(msg["apikey_button"], url="https://dash.cloudflare.com/profile/api-tokens")],
        [InlineKeyboardButton(msg["create_button"], callback_data="start_create")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        msg["language_set"] + "\n\n" + msg["tutorial"],
        reply_markup=reply_markup
    )
    return CHOOSE_LANGUAGE

async def start_create_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = user_data.get(user_id, {}).get("language", "en")
    msg = MESSAGES[lang]
    
    await query.edit_message_text(msg["ask_email"])
    return ASK_EMAIL

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await check_membership(update, context):
        keyboard = [
            [InlineKeyboardButton("Join Channel", url="https://t.me/svdplaylist")],
            [InlineKeyboardButton("I Joined ✅", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "⚠️ You must join our channel to use this bot.",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    
    lang = user_data.get(user_id, {}).get("language", "en")
    msg = MESSAGES[lang]
    
    keyboard = [
        [InlineKeyboardButton(msg["signup_button"], url="https://dash.cloudflare.com/sign-up")],
        [InlineKeyboardButton(msg["signin_button"], url="https://dash.cloudflare.com/login")],
        [InlineKeyboardButton(msg["apikey_button"], url="https://dash.cloudflare.com/profile/api-tokens")],
        [InlineKeyboardButton(msg["create_button"], callback_data="start_create")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(msg["tutorial"], reply_markup=reply_markup)
    return CHOOSE_LANGUAGE

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["email"] = update.message.text
    
    lang = user_data.get(user_id, {}).get("language", "en")
    msg = MESSAGES[lang]
    
    await update.message.reply_text(msg["ask_api"])
    return ASK_API_KEY

async def get_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    api_key = update.message.text
    email = user_data[user_id]["email"]
    
    lang = user_data.get(user_id, {}).get("language", "en")
    msg = MESSAGES[lang]
    
    await update.message.reply_text(msg["deploying"])
    
    try:
        headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key,
            "Content-Type": "application/json"
        }
        
        # Get account ID
        await update.message.reply_text(msg["account_info"])
        acc_response = requests.get("https://api.cloudflare.com/client/v4/accounts", headers=headers)
        if not acc_response.json().get("success"):
            await update.message.reply_text(msg["error"].format(acc_response.json().get('errors', 'Invalid credentials')))
            return ConversationHandler.END
        
        account_id = acc_response.json()["result"][0]["id"]
        
        # Download worker.js
        await update.message.reply_text(msg["downloading"])
        worker_response = requests.get(WORKER_JS_URL)
        worker_script = worker_response.text
        
        # Generate random worker name
        worker_name = f"bpb-panel-{secrets.token_hex(4)}"
        
        # Create KV namespace
        await update.message.reply_text(msg["creating_kv"])
        kv_payload = {"title": f"{worker_name}-kv"}
        kv_response = requests.post(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/storage/kv/namespaces",
            headers=headers,
            json=kv_payload
        )
        
        if not kv_response.json().get("success"):
            await update.message.reply_text(msg["error"].format(kv_response.json().get('errors')))
            return ConversationHandler.END
        
        kv_id = kv_response.json()["result"]["id"]
        
        # Generate UUID, TR_PASS, and SUB_PATH to bind as plain text variables
        generated_uuid = str(uuid.uuid4())
        generated_pass = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
        generated_subpath = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

        # Upload worker with bindings (KV + plain text variables)
        await update.message.reply_text(msg["uploading"])        

        worker_metadata = {
            "main_module": "worker.js",
            "bindings": [
                {
                    "type": "kv_namespace",
                    "name": "kv",
                    "namespace_id": kv_id
                },
                {
                    "type": "plain_text",
                    "name": "UUID",
                    "text": generated_uuid
                },
                {
                    "type": "plain_text",
                    "name": "TR_PASS",
                    "text": generated_pass
                },
                {
                    "type": "plain_text",
                    "name": "SUB_PATH",
                    "text": generated_subpath
                }
            ]
        }

        files = {
            "worker.js": ("worker.js", worker_script, "application/javascript+module"),
            "metadata": ("metadata.json", json.dumps(worker_metadata), "application/json")
        }

        worker_headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key
        }

        upload_response = requests.put(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/scripts/{worker_name}",
            headers=worker_headers,
            files=files
        )

        if not upload_response.json().get("success"):
            await update.message.reply_text(msg["error"].format(upload_response.json().get('errors')))
            return ConversationHandler.END
        
        # Fetch account workers subdomain to build correct URL
        await update.message.reply_text(msg["subdomain"])        
        subdomain_resp = requests.get(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/subdomain",
            headers=headers
        )
        if subdomain_resp.json().get("success") and subdomain_resp.json().get("result"):
            subdomain = subdomain_resp.json()["result"].get("subdomain")
        else:
            subdomain = email.split('@')[0]

        # Enable subdomain
        subdomain_payload = {"enabled": True}
        requests.post(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/scripts/{worker_name}/subdomain",
            headers=headers,
            json=subdomain_payload
        )

        # Get worker URL
        worker_url = f"https://{worker_name}.{subdomain}.workers.dev"
        panel_url = f"{worker_url}/panel"
        
        # Build fragment subscription URL
        fragment_url = f"{worker_url}/sub/fragment/{generated_uuid}?app=xray#%F0%9F%92%A6%20BPB%20Fragment"
        
        await update.message.reply_text(msg["success"].format(panel_url, fragment_url), parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(msg["error"].format(str(e)))
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("create", create)],
        states={
            CHOOSE_LANGUAGE: [
                CallbackQueryHandler(check_membership_callback, pattern="^check_membership$"),
                CallbackQueryHandler(language_callback, pattern="^lang_"),
                CallbackQueryHandler(start_create_callback, pattern="^start_create$")
            ],
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            ASK_API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_api_key)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )
    
    application.add_handler(conv_handler)
    
    print("Bot started...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
