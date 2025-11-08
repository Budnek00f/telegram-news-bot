import schedule
import time
import logging
from datetime import datetime
from news_parser import NewsParser
from bot import TelegramNewsBot
import os
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NewsScheduler:
    def __init__(self):
        try:
            logger.info("🔄 Инициализация компонентов...")
            self.news_parser = NewsParser()
            self.telegram_bot = TelegramNewsBot()
            self.post_count = 0
            logger.info("✅ NewsScheduler инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации NewsScheduler: {e}")
            raise

    def post_news(self):
        """Создает и публикует новость"""
        try:
            logger.info("🚀 Поиск актуальных IT-новостей...")
            
            # Получаем случайную IT-новость
            news_item = self.news_parser.get_random_it_news()
            
            # Форматируем для Telegram
            news_text = self.news_parser.format_news_for_telegram(news_item)
            image_url = self.news_parser.get_news_image(news_item)
            
            logger.info(f"✅ Новость получена: {news_item['title'][:50]}...")
            logger.info(f"🖼️ Изображение: {image_url}")
            
            # Публикуем в канал
            success = self.telegram_bot.send_news_to_channel(news_text, image_url)
            
            if success:
                self.post_count += 1
                logger.info(f"✅ Новость #{self.post_count} успешно опубликована в {datetime.now()}")
            else:
                logger.error("❌ Не удалось опубликовать новость")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при публикации новости: {e}")

    def run_scheduler(self):
        """Запускает планировщик"""
        logger.info("🔄 Запуск планировщика новостей...")
        
        # Настраиваем расписание
        schedule.every(15).minutes.do(self.post_news)      
        
        logger.info("⏰ Планировщик настроен: каждые 20 мин (тест) и каждый час")
        
        # Первая публикация при запуске
        logger.info("🎯 Первая публикация...")
        self.post_news()
        
        logger.info("🔄 Планировщик запущен, ожидание задач...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(30)
            except KeyboardInterrupt:
                logger.info("🛑 Планировщик остановлен пользователем")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в основном цикле: {e}")
                time.sleep(30)

def main():
    """Основная функция"""
    try:
        logger.info("🚀 Запуск Telegram News Parser Bot...")
        
        # Проверяем переменные окружения
        required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHANNEL_ID']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
            sys.exit(1)
        
        logger.info("✅ Все переменные окружения присутствуют")
        
        # Создаем и запускаем планировщик
        scheduler = NewsScheduler()
        scheduler.run_scheduler()
        
    except KeyboardInterrupt:
        logger.info("🛑 Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка при запуске: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
