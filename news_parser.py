import os
import logging
import requests
import feedparser
import random
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
import time
import pytz

logger = logging.getLogger(__name__)

class NewsParser:
    def __init__(self):
        self.news_sources = [
            # IT-новости на русском
            {
                'name': 'VC.ru IT',
                'url': 'https://vc.ru/rss/new',
                'category': 'it'
            },
            {
                'name': 'TJournal Tech',
                'url': 'https://tjournal.ru/rss',
                'category': 'tech'
            },
            {
                'name': 'Habr',
                'url': 'https://habr.com/ru/rss/articles/?fl=ru',
                'category': 'development'
            },
            {
                'name': 'IXBT',
                'url': 'https://www.ixbt.com/export/news.rss',
                'category': 'tech'
            },
            {
                'name': 'CNews',
                'url': 'https://www.cnews.ru/inc/rss/news.xml',
                'category': 'it'
            }
        ]
        
        # Ключевые слова для фильтрации IT-новостей
        self.it_keywords = [
            'искусственный интеллект', 'AI', 'машинное обучение', 'нейросеть',
            'программирование', 'разработка', 'IT', 'технологии', 'софт',
            'кибербезопасность', 'хакер', 'вирус', 'защита данных',
            'облако', 'cloud', 'DevOps', 'база данных', 'SQL', 'NoSQL',
            'мобильное приложение', 'iOS', 'Android', 'React', 'Vue',
            'блокчейн', 'криптовалюта', 'биткоин', 'NFT',
            'игры', 'геймдев', 'Unity', 'Unreal Engine',
            'аналитика', 'Big Data', 'data science', 'ML',
            'интернет вещей', 'IoT', 'умный дом', 'автоматизация',
            'стартап', 'инвестиции', 'венчур', 'техстартап',
            'Microsoft', 'Google', 'Apple', 'Amazon', 'Meta',
            'Python', 'JavaScript', 'Java', 'C++', 'Go', 'Rust'
        ]
        
        logger.info("✅ NewsParser инициализирован")

    def fetch_news_from_rss(self, source):
        """Парсит новости из RSS ленты"""
        try:
            logger.info(f"📡 Загрузка новостей из {source['name']}...")
            feed = feedparser.parse(source['url'])
            
            news_items = []
            for entry in feed.entries[:15]:  # Берем последние 15 новостей
                # Проверяем, что новость свежая (не старше 7 дней)
                published_time = self._parse_date(entry.get('published', ''))
                if not self._is_recent(published_time):
                    continue
                
                # Проверяем, что новость относится к IT
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                if self._is_it_news(title + ' ' + summary):
                    news_item = {
                        'title': title,
                        'link': entry.link,
                        'summary': summary,
                        'published': published_time,
                        'source': source['name'],
                        'image': self._extract_image(entry)
                    }
                    news_items.append(news_item)
            
            logger.info(f"✅ Найдено {len(news_items)} IT-новостей из {source['name']}")
            return news_items
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга {source['name']}: {e}")
            return []

    def _parse_date(self, date_str):
        """Парсит дату из различных форматов"""
        try:
            if not date_str:
                return datetime.now(pytz.UTC)
            
            # Пробуем разные форматы дат
            try:
                # Стандартный формат RSS
                parsed_date = feedparser._parse_date(date_str)
                if parsed_date:
                    return parsed_date
            except:
                pass
            
            # Если не получилось, возвращаем текущую дату
            return datetime.now(pytz.UTC)
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка парсинга даты '{date_str}': {e}")
            return datetime.now(pytz.UTC)

    def _is_recent(self, date_obj):
        """Проверяет, что новость свежая (не старше 7 дней)"""
        if not date_obj:
            return True
            
        now = datetime.now(pytz.UTC)
        if hasattr(date_obj, 'tzinfo') and date_obj.tzinfo is not None:
            # Дата с часовым поясом
            time_diff = now - date_obj
        else:
            # Дата без часового пояса
            time_diff = now - date_obj.replace(tzinfo=pytz.UTC)
        
        return time_diff.days <= 7

    def _is_it_news(self, text):
        """Проверяет, относится ли новость к IT"""
        if not text:
            return False
            
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.it_keywords)

    def _extract_image(self, entry):
        """Извлекает изображение из RSS записи"""
        try:
            # Пробуем разные способы извлечения изображения
            if hasattr(entry, 'media_content') and entry.media_content:
                for media in entry.media_content:
                    if media.get('type', '').startswith('image/'):
                        return media['url']
            
            if hasattr(entry, 'links'):
                for link in entry.links:
                    if link.get('type', '').startswith('image/'):
                        return link['href']
            
            # Пробуем извлечь из описания
            if hasattr(entry, 'summary'):
                soup = BeautifulSoup(entry.summary, 'html.parser')
                img = soup.find('img')
                if img and img.get('src'):
                    return img['src']
            
            # Для Habr - специальная обработка
            if 'habr.com' in entry.get('link', ''):
                return self._get_habr_image(entry)
                
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка извлечения изображения: {e}")
            return None

    def _get_habr_image(self, entry):
        """Получает изображение для Habr статьи"""
        try:
            # Habr часто хранит изображения в content
            if hasattr(entry, 'content'):
                for content in entry.content:
                    soup = BeautifulSoup(content.value, 'html.parser')
                    img = soup.find('img')
                    if img and img.get('src'):
                        return img['src']
            return None
        except:
            return None

    def get_random_it_news(self):
        """Получает случайную IT-новость из всех источников"""
        all_news = []
        
        for source in self.news_sources:
            try:
                news_items = self.fetch_news_from_rss(source)
                all_news.extend(news_items)
                time.sleep(0.5)  # Короткая задержка между запросами
            except Exception as e:
                logger.error(f"❌ Ошибка при получении новостей из {source['name']}: {e}")
                continue
        
        if not all_news:
            logger.warning("⚠️ Не найдено IT-новостей, используем резервные")
            return self._get_fallback_news()
        
        # Выбираем случайную новость
        selected_news = random.choice(all_news)
        logger.info(f"🎲 Выбрана новость: {selected_news['title'][:50]}...")
        
        return selected_news

    def _get_fallback_news(self):
        """Резервные новости если парсинг не сработал"""
        fallback_news = [
            {
                'title': 'Искусственный интеллект в разработке ПО',
                'summary': 'Компании активно внедряют AI для автоматизации тестирования и генерации кода. Новые инструменты позволяют ускорить разработку на 30%.',
                'link': 'https://habr.com/ru/articles/',
                'source': 'IT News',
                'image': None
            },
            {
                'title': 'Кибербезопасность в 2024 году',
                'summary': 'Эксперты прогнозируют рост атак на облачную инфраструктуру. Компании инвестируют в новые системы защиты данных.',
                'link': 'https://vc.ru/tech',
                'source': 'Security Digest',
                'image': None
            },
            {
                'title': 'Тренды мобильной разработки',
                'summary': 'Flutter и React Native продолжают доминировать в кроссплатформенной разработке. Растет популярность PWA приложений.',
                'link': 'https://tjournal.ru/tech',
                'source': 'Mobile World',
                'image': None
            }
        ]
        
        return random.choice(fallback_news)

    def format_news_for_telegram(self, news_item):
        """Форматирует новость для Telegram"""
        title = news_item['title']
        summary = news_item['summary']
        source = news_item['source']
        link = news_item['link']
        
        # Очищаем текст от HTML тегов
        clean_summary = re.sub('<[^<]+?>', '', summary)
        clean_summary = clean_summary.replace('&nbsp;', ' ').replace('&quot;', '"')
        clean_summary = clean_summary[:400] + '...' if len(clean_summary) > 400 else clean_summary
        
        # Создаем форматированный текст
        formatted_text = f"""🚀 <b>{title}</b>

{clean_summary}

📰 <i>Источник: {source}</i>
🔗 <a href="{link}">Читать подробнее</a>

#ITновости #Технологии #Разработка"""
        
        return formatted_text

    def get_news_image(self, news_item):
        """Возвращает изображение для новости"""
        # Сначала пробуем получить изображение из новости
        if news_item.get('image'):
            # Проверяем, что URL валидный
            image_url = news_item['image']
            if image_url.startswith(('http://', 'https://')):
                return image_url
        
        # Если изображения нет, используем локальные заглушки или тематические
        image_themes = {
            'искусственный интеллект': '🤖',
            'кибербезопасность': '🔐', 
            'программирование': '💻',
            'мобильная разработка': '📱',
            'облако': '☁️',
            'блокчейн': '⛓️',
            'аналитика': '📊',
            'игры': '🎮'
        }
        
        # Ищем тему по ключевым словам
        text = (news_item['title'] + ' ' + news_item['summary']).lower()
        for theme, emoji in image_themes.items():
            if theme in text:
                # Используем эмодзи как "изображение" - None означает без картинки
                return None
                
        # Если не нашли тему, без изображения
        return None
