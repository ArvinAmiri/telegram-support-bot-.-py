import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
#logging.basicConfig(level=logging.ERROR)

ADMINS = [0000000] #change it to user number id

pending_replies = {}
WAITING_FOR_REPLY = 1

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    if user.id in ADMINS:
        return

    await message.reply_text("✅ پیام شما برای پشتیبان ارسال شد. لطفاً منتظر بمانید...")

    for admin_id in ADMINS:
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"📨 پیام جدید از {user.full_name} (ID: {user.id}):\n\n{message.text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 پاسخ", callback_data=f"reply:{user.id}")]
            ])
        )

async def handle_reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    admin_id = query.from_user.id
    data = query.data

    if data.startswith("reply:"):
        user_id = int(data.split(":")[1])
        pending_replies[admin_id] = user_id

        await query.message.reply_text("✏️ لطفاً پاسخ خود را بنویسید:")
        return WAITING_FOR_REPLY

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    message = update.message

    if admin_id not in pending_replies:
        await message.reply_text("⛔ ابتدا باید روی دکمه «📩 پاسخ» در پیام کاربر کلیک کنید.")
        return ConversationHandler.END

    user_id = pending_replies.pop(admin_id)

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📬 پاسخ پشتیبان:\n\n{message.text}"
        )
        await message.reply_text("✅ پیام شما به کاربر ارسال شد.")
    except Exception as e:
        await message.reply_text(f"❌ ارسال پیام به کاربر ناموفق بود.\nخطا: {e}")

    return ConversationHandler.END

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! پیام خود را برای پشتیبان ارسال کنید.")

def main():
    app = ApplicationBuilder().token("TOKEN").build() #paste your token here


    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_reply_button, pattern="^reply:")],
        states={
            WAITING_FOR_REPLY: [MessageHandler(filters.TEXT & (~filters.COMMAND), handle_admin_reply)]
        },
        fallbacks=[],
        per_chat=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_user_message))
    app.run_polling()

if __name__ == "__main__":
    main()