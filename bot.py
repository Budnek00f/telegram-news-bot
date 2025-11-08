import os
import logging
import requests
import tempfile

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramNewsBot:
    def __init__(self):
        try:
            self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
            
            if not self.bot_token:
                raise ValueError("TELEGRAM_BOT_TOKEN не установлен")
            if not self.channel_id:
                raise ValueError("TELEGRAM_CHANNEL_ID не установлен")
                
            self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
            logger.info("✅ Telegram бот инициализирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Telegram бота: {e}")
            raise
        
    def send_news_to_channel(self, news_text, image_url=None):
        """Отправляет новость в канал с изображением"""
        try:
            logger.info(f"📤 Отправка новости в канал {self.channel_id}...")
            
            if image_url:
                logger.info(f"🖼️ Попытка отправить с изображением: {image_url}")
                success = self._send_photo_with_caption(news_text, image_url)
                if success:
                    return True
                else:
                    logger.warning("⚠️ Не удалось отправить с изображением, пробуем без него")
            
            # Если изображение недоступно, отправляем только текст
            logger.info("📝 Отправка текстовой новости...")
            return self._send_text_message(news_text)
                
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке сообщения: {e}")
            return False

    def _send_photo_with_caption(self, caption, image_url):
        """Отправляет фото с подписью"""
        try:
            # Скачиваем изображение
            response = requests.get(image_url, timeout=15)
            if response.status_code != 200:
                return False
            
            # Сохраняем временно и отправляем
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            # Отправляем через multipart/form-data
            url = f"{self.base_url}/sendPhoto"
            files = {'photo': open(temp_file_path, 'rb')}
            data = {
                'chat_id': self.channel_id,
                'caption': caption[:1024],  # Ограничение Telegram
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, files=files, data=data, timeout=30)
            result = response.json()
            
            # Удаляем временный файл
            os.unlink(temp_file_path)
            
            if result.get('ok'):
                logger.info("✅ Новость с изображением отправлена в канал")
                return True
            else:
                logger.error(f"❌ Ошибка отправки фото: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке фото: {e}")
            return False

    def _send_text_message(self, text):
        """Отправляет текстовое сообщение"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.channel_id,
                "text": text[:4096],  # Ограничение Telegram
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            
            response = requests.post(url, json=payload, timeout=30)
            result = response.json()
            
            if result.get('ok'):
                logger.info("✅ Текстовая новость отправлена в канал")
                return True
            else:
                logger.error(f"❌ Ошибка Telegram API: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке текста: {e}")
            return False