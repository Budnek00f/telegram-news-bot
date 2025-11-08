import schedule
import time
import logging
from datetime import datetime, timedelta
from news_parser import NewsParser
from bot import TelegramNewsBot
import os
import sys

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
            self.last_news_titles = set()
            logger.info("✅ NewsScheduler инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации NewsScheduler: {e}")
            raise

    def post_news(self):
        """Создает и публикует новость с фото"""
        try:
            logger.info("🚀 Поиск актуальных IT-новостей...")
            
            news_item = self.news_parser.get_random_it_news()
            
            news_title = news_item['title']
            if news_title in self.last_news_titles:
                logger.info("🔄 Найдена дублирующаяся новость, ищем другую...")
                news_item = self.news_parser.get_random_it_news()
                news_title = news_item['title']
            
            self.last_news_titles.add(news_title)
            if len(self.last_news_titles) > 100:  # Увеличили кэш для 30-минутного интервала
                self.last_news_titles.remove(next(iter(self.last_news_titles)))
            
            # Форматируем новость
            news_text = self.news_parser.format_news_for_telegram(news_item)
            image_url = self.news_parser.get_news_image(news_item)
            
            logger.info(f"✅ Новость получена: {news_item['title'][:50]}...")
            logger.info(f"🖼️ Изображение: {'Есть' if image_url else 'Нет'}")
            
            # Публикуем в канал
            success = self.telegram_bot.send_news_to_channel(news_text, image_url)
            
            if success:
                self.post_count += 1
                current_time = datetime.now().strftime("%H:%M:%S")
                logger.info(f"✅ Новость #{self.post_count} отправлена в {current_time}")
                
                next_time = datetime.now() + timedelta(minutes=30)
                next_time_str = next_time.strftime("%H:%M")
                logger.info(f"⏰ Следующая новость в {next_time_str}")
            else:
                logger.error("❌ Не удалось опубликовать новость")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при публикации новости: {e}")

    def run_scheduler(self):
        """Запускает планировщик"""
        logger.info("🔄 Запуск планировщика новостей...")
        logger.info("🎯 Немедленная публикация первой новости...")
        self.post_news()
        
        # Настраиваем на 30 минут
        schedule.every(30).minutes.do(self.post_news)
        
        logger.info("⏰ Планировщик настроен: каждые 30 минут")
        logger.info("🔄 Планировщик запущен...")
        
        while True:
            try:
                schedule.run_pending()
                
                # Логируем статус каждые 10 минут
                next_job = schedule.next_run()
                if next_job:
                    time_left = next_job - datetime.now()
                    minutes_left = int(time_left.total_seconds() / 60)
                    if minutes_left % 10 == 0:  # Логируем каждые 10 минут
                        logger.info(f"⏳ До следующей новости: {minutes_left} минут")
                
                time.sleep(60)  # Проверяем каждую минуту
                
            except KeyboardInterrupt:
                logger.info("🛑 Планировщик остановлен")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка: {e}")
                time.sleep(60)

if __name__ == "__main__":
    try:
        logger.info("🚀 Запуск IT News Bot (30 минут, с фото)")
        scheduler = NewsScheduler()
        scheduler.run_scheduler()
    except Exception as e:
        logger.error(f"💥 Ошибка: {e}")
        sys.exit(1)
