import os
import asyncio
import uuid
import secrets
import string
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8244225523:AAGkQRMRuBV4dg8hvnys6z6jtvH88UPfN_E")

ASK_EMAIL, ASK_API_KEY = range(2)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to BPB Worker Panel Bot!\n\n"
        "Use /create to deploy BPB Worker Panel to Cloudflare"
    )

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter your Cloudflare email address:")
    return ASK_EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"email": update.message.text}
    await update.message.reply_text("Please enter your Cloudflare API Key:")
    return ASK_API_KEY

async def get_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    api_key = update.message.text
    email = user_data[user_id]["email"]
    
    await update.message.reply_text("🚀 Starting deployment...\nThis may take a few minutes.")
    
    try:
        headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key,
            "Content-Type": "application/json"
        }
        
        # Get account ID
        await update.message.reply_text("📋 Getting account information...")
        acc_response = requests.get("https://api.cloudflare.com/client/v4/accounts", headers=headers)
        if not acc_response.json().get("success"):
            await update.message.reply_text(f"❌ Error: {acc_response.json().get('errors', 'Invalid credentials')}")
            return ConversationHandler.END
        
        account_id = acc_response.json()["result"][0]["id"]
        
        # Download worker.js
        await update.message.reply_text("📥 Downloading worker script...")
        worker_response = requests.get("https://github.com/bia-pain-bache/BPB-Worker-Panel/releases/download/v3.6.1/worker.js")
        worker_script = worker_response.text
        
        # Generate random worker name
        worker_name = f"bpb-panel-{secrets.token_hex(4)}"
        
        # Create KV namespace
        await update.message.reply_text("🗄️ Creating KV namespace...")
        kv_payload = {"title": f"{worker_name}-kv"}
        kv_response = requests.post(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/storage/kv/namespaces",
            headers=headers,
            json=kv_payload
        )
        
        if not kv_response.json().get("success"):
            await update.message.reply_text(f"❌ KV Error: {kv_response.json().get('errors')}")
            return ConversationHandler.END
        
        kv_id = kv_response.json()["result"]["id"]
        
        # Upload worker
        await update.message.reply_text("☁️ Uploading worker to Cloudflare...")
        
        worker_metadata = {
            "main_module": "worker.js",
            "bindings": [
                {
                    "type": "kv_namespace",
                    "name": "kv",
                    "namespace_id": kv_id
                }
            ]
        }
        
        files = {
            "worker.js": ("worker.js", worker_script, "application/javascript+module"),
            "metadata": ("metadata.json", str(worker_metadata).replace("'", '"'), "application/json")
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
            await update.message.reply_text(f"❌ Upload Error: {upload_response.json().get('errors')}")
            return ConversationHandler.END
        
        # Generate UUID and TR_PASS
        generated_uuid = str(uuid.uuid4())
        generated_pass = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
        
        # Set secrets
        await update.message.reply_text("🔐 Setting up secrets...")
        
        secrets_data = {
            "UUID": generated_uuid,
            "TR_PASS": generated_pass
        }
        
        for secret_name, secret_value in secrets_data.items():
            secret_payload = {
                "name": secret_name,
                "text": secret_value,
                "type": "secret_text"
            }
            requests.put(
                f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/scripts/{worker_name}/secrets",
                headers=headers,
                json=secret_payload
            )
        
        # Create subdomain
        await update.message.reply_text("🌐 Creating worker subdomain...")
        subdomain_payload = {
            "enabled": True
        }
        requests.post(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/scripts/{worker_name}/subdomain",
            headers=headers,
            json=subdomain_payload
        )
        
        # Get worker URL
        worker_url = f"https://{worker_name}.{email.split('@')[0]}.workers.dev"
        
        result_message = (
            "✅ Deployment completed successfully!\n\n"
            f"🔗 Worker URL: {worker_url}\n"
            f"📝 Worker Name: {worker_name}\n"
            f"🔑 UUID: `{generated_uuid}`\n"
            f"🔐 Trojan Password: `{generated_pass}`\n\n"
            "Open your worker URL to access the panel!"
        )
        
        await update.message.reply_text(result_message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create", create)],
        states={
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            ASK_API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_api_key)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    
    print("Bot started...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
