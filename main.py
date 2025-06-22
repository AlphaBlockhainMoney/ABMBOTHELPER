### main.py — основной файл Telegram-бота

import json
import os
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes,
    filters, ConversationHandler
)
from eth_helpers import is_valid_eth_address, get_token_balance
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = "8163047082:AAHXyQwv_oXIC8JcqPGlEH9ywtUJuVSQmcY"
USERS_FILE = "users.json"
BUY_URL = "https://abm-site-bot.vercel.app"

SET_ADDRESS = 0

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# --- Главное меню ---
def main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📍 Сеть"), KeyboardButton("💼 Баланс")],
        [KeyboardButton("🛒 Купить ABM"), KeyboardButton("💸 Продать ABM")],
        [KeyboardButton("ℹ️ О токене")]
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    if user_id not in users:
        users[user_id] = {
            "username": update.effective_user.username or "",
            "address": None,
            "network": None
        }
        save_users(users)
    await update.message.reply_text(
        "Добро пожаловать в мир ABM! 🔵\nВыберите сеть для начала:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Sepolia", callback_data="network_sepolia"),
             InlineKeyboardButton("Ethereum Mainnet", callback_data="network_mainnet")]
        ])
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    users = load_users()

    if query.data.startswith("network_"):
        network = query.data.replace("network_", "")
        users[user_id]["network"] = network
        save_users(users)
        await query.edit_message_text(f"✅ Сеть выбрана: {network.title()}\nТеперь отправьте свой Ethereum адрес.")
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    users = load_users()

    if user_id not in users or not users[user_id].get("network"):
        await update.message.reply_text("Пожалуйста, сначала выберите сеть: /start")
        return

    if is_valid_eth_address(text):
        users[user_id]["address"] = text
        save_users(users)
        await update.message.reply_text("✅ Адрес сохранён! Используйте меню ниже.", reply_markup=main_menu())
        return

    if text == "📍 Сеть":
        await update.message.reply_text(
            "Выберите сеть:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Sepolia", callback_data="network_sepolia"),
                 InlineKeyboardButton("Ethereum Mainnet", callback_data="network_mainnet")]
            ])
        )

    elif text == "💼 Баланс":
        user = users.get(user_id, {})
        network = user.get("network")
        address = user.get("address")
        if not address:
            await update.message.reply_text("Сначала отправьте ваш Ethereum адрес.")
            return
        if network == "mainnet":
            await update.message.reply_text(
                "ℹ️ Токен ABM пока не развернут в сети Ethereum Mainnet.\nОн не имеет рыночной ценности и не может быть проверен на баланс.")
        else:
            try:
                balance, symbol = get_token_balance(address, network)
                await update.message.reply_text(f"Ваш баланс: {balance:.4f} {symbol}")
            except Exception as e:
                await update.message.reply_text(f"Ошибка: {e}")

    elif text == "🛒 Купить ABM":
        await update.message.reply_text("Открываем приложение покупки ABM:",
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("Купить ABM", web_app=WebAppInfo(url=BUY_URL))]
                                        ]))

    elif text == "💸 Продать ABM":
        await update.message.reply_text("Продажа временно недоступна. 💼\nТокен ABM скоро появится на Ethereum Mainnet и будет доступен для торговли.")

    elif text == "ℹ️ О токене":
        info = (
            "💠 *ABM (Alpha Blockchain Money)*\n"
            "Версия: 1\n"
            "Общее количество токенов: 1,000,000,000 ABM\n"
            "GitHub: [AlphaBlockhainMoney](https://github.com/AlphaBlockhainMoney)\n"
            "Telegram канал: [@Abmcoin_RUS](https://t.me/Abmcoin_RUS)\n"
            "Контакт для сотрудничества: @ThermoFisherScientifis\n\n"
            "🌐 ABM — это токен нового поколения, обеспечивающий свободу, прозрачность и доступность."
        )
        await update.message.reply_text(info, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
