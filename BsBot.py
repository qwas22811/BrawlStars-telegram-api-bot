from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import requests

telegram_token = 'Your telegram token should be here'
api_key = 'Your Brawl Stars api token should be here'

headers = {
    "Authorization": f"Bearer {api_key}",
}

def get_player_data(player_tag):
    url = f"https://api.brawlstars.com/v1/players/%23{player_tag}"
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Войти в профиль", callback_data="enter_profile")],
        [InlineKeyboardButton("📊 Посмотреть информацию", callback_data="view_info")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Привет! Я бот Brawl Stars. Тут ты можешь посмотреть статистику своего профиля!",
        reply_markup=reply_markup,
    )

async def enter_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✍️ Введите ваш тег (без #):")
    context.user_data["awaiting_tag"] = True

async def save_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_tag"):
        player_tag = update.message.text.strip()
        context.user_data["player_tag"] = player_tag
        context.user_data["awaiting_tag"] = False
        
        keyboard = [
            [InlineKeyboardButton("📊 Посмотреть информацию", callback_data="view_info")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("✅ Ваш профиль сохранен!", reply_markup=reply_markup)

async def view_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    player_tag = context.user_data.get("player_tag")
    if not player_tag:
        await query.edit_message_text(
            "❌ Профиль не установлен. Пожалуйста, сначала войдите в профиль.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎮 Войти в профиль", callback_data="enter_profile")]])
        )
        return

    player_data = get_player_data(player_tag)
    if player_data:
        player_name = player_data.get("name", "Неизвестно")
        trophies = player_data.get("trophies", "Нет данных")
        clan_name = player_data.get("club", {}).get("name", "Вы не в клане")
        
        await update.callback_query.message.reply_text(
            f"📋 Информация профиля:\n👤 Имя: {player_name}\n🏆 Трофеи: {trophies}\n🏰 Клан: {clan_name}"
        )
        
        keyboard = [
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="return_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(
            "⬅️ Нажмите кнопку ниже, чтобы вернуться в главное меню.",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text("❌ Ошибка получения данных. Проверьте тег.",
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎮 Войти в профиль", callback_data="enter_profile")]]))

async def return_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🎮 Войти в профиль", callback_data="enter_profile")],
        [InlineKeyboardButton("📊 Посмотреть информацию", callback_data="view_info")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "👋 Привет! Я бот Brawl Stars.\nВыберите действие:",
        reply_markup=reply_markup,
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(telegram_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(enter_profile, pattern="enter_profile"))
    app.add_handler(CallbackQueryHandler(view_info, pattern="view_info"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_tag))
    app.add_handler(CallbackQueryHandler(return_to_menu, pattern="return_to_menu"))

    print("Бот запущен")
    app.run_polling()
