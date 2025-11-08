import os
from telegram import Bot

def check_bot():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    
    print(f"Bot Token: {bot_token[:10]}...")
    print(f"Channel ID from env: {channel_id}")
    
    bot = Bot(token=bot_token)
    
    # Попробуем получить информацию о канале
    try:
        chat = bot.get_chat(channel_id)
        print(f"Channel info: {chat}")
        print(f"Channel title: {chat.title}")
        print(f"Channel username: {chat.username}")
    except Exception as e:
        print(f"Error getting channel info: {e}")
    
    # Попробуем отправить тестовое сообщение
    try:
        message = bot.send_message(
            chat_id=channel_id,
            text="🤖 <b>Тестовое сообщение от бота</b>\n\nЕсли вы это видите, бот работает правильно!",
            parse_mode='HTML'
        )
        print(f"✅ Тестовое сообщение отправлено! Message ID: {message.message_id}")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

if __name__ == "__main__":
    check_bot()