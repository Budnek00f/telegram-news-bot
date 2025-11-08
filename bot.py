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
        """Отправляет новость в канал"""
        try:
            logger.info(f"📤 Отправка новости в канал {self.channel_id}...")
            
            # Если есть изображение и оно локальное (не внешняя ссылка), пробуем отправить
            if image_url and self._is_local_image(image_url):
                logger.info(f"🖼️ Попытка отправить с локальным изображением")
                success = self._send_photo_with_caption(news_text, image_url)
                if success:
                    return True
            
            # Всегда отправляем текстовую версию (надежнее)
            logger.info("📝 Отправка текстовой новости...")
            return self._send_text_message(news_text)
                
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке сообщения: {e}")
            return False

    def _is_local_image(self, image_url):
        """Проверяет, является ли изображение локальным файлом"""
        return image_url and not image_url.startswith(('http://', 'https://'))

    def _send_photo_with_caption(self, caption, image_path):
        """Отправляет фото с подписью"""
        try:
            if not os.path.exists(image_path):
                return False
                
            url = f"{self.base_url}/sendPhoto"
            files = {'photo': open(image_path, 'rb')}
            data = {
                'chat_id': self.channel_id,
                'caption': caption[:1024],
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, files=files, data=data, timeout=30)
            result = response.json()
            
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
                "text": text[:4096],
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
