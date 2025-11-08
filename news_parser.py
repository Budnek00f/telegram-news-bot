import os
import logging
import requests
import feedparser
import random
from datetime import datetime, timezone
import re
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)

class NewsParser:
    def __init__(self):
        self.news_sources = [
            {
                'name': 'Habr',
                'url': 'https://habr.com/ru/rss/articles/?fl=ru',
                'category': 'development'
            },
            {
                'name': 'VC.ru Tech',
                'url': 'https://vc.ru/rss/new',
                'category': 'tech'
            },
            {
                'name': 'TJournal Tech',
                'url': 'https://tjournal.ru/rss',
                'category': 'tech'
            },
            {
                'name': 'IXBT News',
                'url': 'https://www.ixbt.com/export/news.rss',
                'category': 'hardware'
            }
        ]
        
        self.strict_it_keywords = [
            'программирование', 'разработка', 'код', 'алгоритм', 'фреймворк',
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'PHP',
            'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask',
            'Git', 'GitHub', 'GitLab', 'Docker', 'Kubernetes',
            'искусственный интеллект', 'AI', 'машинное обучение', 'ML',
            'нейросеть', 'нейросети', 'deep learning', 'data science',
            'аналитика данных', 'Big Data', 'база данных', 'SQL', 'NoSQL',
            'кибербезопасность', 'безопасность', 'хакер', 'вирус',
            'защита данных', 'шифрование', 'VPN', 'firewall',
            'облако', 'cloud', 'DevOps', 'микросервисы', 'API',
            'мобильное приложение', 'iOS', 'Android', 'React Native', 'Flutter',
            'веб-разработка', 'frontend', 'backend', 'fullstack', 'HTML', 'CSS',
            'блокчейн', 'криптовалюта', 'биткоин', 'Ethereum', 'NFT', 'Web3',
            'геймдев', 'игровой движок', 'Unity', 'Unreal Engine', 'VR', 'AR'
        ]
        
        logger.info("✅ NewsParser инициализирован")

    def fetch_news_from_rss(self, source):
        """Парсит новости из RSS ленты"""
        try:
            logger.info(f"📡 Загрузка новостей из {source['name']}...")
            feed = feedparser.parse(source['url'])
            
            news_items = []
            for entry in feed.entries[:20]:
                published_time = self._parse_date(entry)
                if not self._is_recent(published_time):
                    continue
                
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                full_text = title + ' ' + summary
                
                if self._is_strict_it_news(full_text):
                    # Получаем полный текст
                    full_content = self._get_full_content(entry, source)
                    
                    news_item = {
                        'title': self._clean_title(title),
                        'link': entry.link,
                        'summary': self._shorten_summary(summary, 300),  # Более длинное описание
                        'full_text': full_content,
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

    def _get_full_content(self, entry, source):
        """Получает полный текст новости"""
        try:
            # Используем контент из RSS если доступен
            if hasattr(entry, 'content') and entry.content:
                full_text = ''
                for content in entry.content:
                    if hasattr(content, 'value'):
                        soup = BeautifulSoup(content.value, 'html.parser')
                        text = soup.get_text()
                        full_text += text + '\n\n'
                return self._clean_text(full_text.strip())
            
            # Или используем summary как полный текст
            summary = entry.get('summary', '')
            if summary:
                return self._clean_text(summary)
            
            return entry.get('title', '')
            
        except Exception as e:
            logger.warning(f"⚠️ Не удалось получить полный текст: {e}")
            return entry.get('summary', entry.get('title', ''))

    def _clean_text(self, text):
        """Очищает текст от HTML и лишних пробелов"""
        if not text:
            return ""
        
        clean_text = re.sub('<[^<]+?>', '', text)
        clean_text = clean_text.replace('&nbsp;', ' ').replace('&quot;', '"')
        clean_text = clean_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text

    def _parse_date(self, entry):
        """Парсит дату из RSS записи"""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            return datetime.now(timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)

    def _is_recent(self, date_obj):
        """Проверяет, что новость свежая"""
        if not date_obj:
            return True
        now = datetime.now(timezone.utc)
        if date_obj.tzinfo is None:
            date_obj = date_obj.replace(tzinfo=timezone.utc)
        time_diff = now - date_obj
        return time_diff.days <= 3  # Увеличили до 3 дней для 30-минутного интервала

    def _is_strict_it_news(self, text):
        """Строгая проверка на IT-тематику"""
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.strict_it_keywords)

    def _shorten_summary(self, text, max_length=300):
        """Сокращает текст для описания"""
        if not text:
            return "Интересная IT-новость. Нажмите на фото для чтения полной версии."
        
        clean_text = self._clean_text(text)
        
        if len(clean_text) > max_length:
            shortened = clean_text[:max_length]
            last_dot = shortened.rfind('.')
            if last_dot > max_length * 0.6:
                return shortened[:last_dot + 1]
            else:
                return shortened + '...'
        
        return clean_text

    def _clean_title(self, title):
        """Очищает заголовок"""
        if not title:
            return ""
        return re.sub(r'\s+', ' ', title).strip()

    def _extract_image(self, entry):
        """Извлекает изображение из RSS записи"""
        try:
            if hasattr(entry, 'media_content') and entry.media_content:
                for media in entry.media_content:
                    if media.get('type', '').startswith('image/'):
                        return media['url']
            
            if hasattr(entry, 'links'):
                for link in entry.links:
                    if link.get('type', '').startswith('image/'):
                        return link.get('href')
            
            if hasattr(entry, 'summary'):
                soup = BeautifulSoup(entry.summary, 'html.parser')
                img = soup.find('img')
                if img and img.get('src'):
                    return img['src']
            
            return None
            
        except Exception:
            return None

    def get_random_it_news(self):
        """Получает случайную IT-новость"""
        all_news = []
        
        for source in self.news_sources:
            try:
                news_items = self.fetch_news_from_rss(source)
                all_news.extend(news_items)
                time.sleep(0.3)
            except Exception as e:
                logger.error(f"❌ Ошибка при получении новостей из {source['name']}: {e}")
                continue
        
        if not all_news:
            logger.warning("⚠️ Не найдено IT-новостей, используем резервные")
            return self._get_fallback_news()
        
        selected_news = random.choice(all_news)
        logger.info(f"🎲 Выбрана новость: {selected_news['title'][:50]}...")
        
        return selected_news

    def _get_fallback_news(self):
        """Резервные новости"""
        fallback_news = {
            'title': 'Новости IT индустрии',
            'summary': 'Актуальные новости из мира технологий и программирования.',
            'full_text': 'В мире IT постоянно происходят интересные события. Следите за обновлениями, чтобы быть в курсе последних тенденций в разработке, искусственном интеллекте и технологиях.',
            'link': 'https://t.me/deeploy_online',
            'source': 'IT News',
            'image': None
        }
        
        return fallback_news

    def format_news_for_telegram(self, news_item):
        """Форматирует полную новость для Telegram"""
        title = news_item['title']
        summary = news_item['summary']
        source = news_item['source']
        link = news_item['link']
        
        formatted_text = f"""🚀 <b>{title}</b>

{summary}

📰 <i>Источник: {source}</i>
🔗 <a href="{link}">Читать подробнее</a>

💫 <i>При нажатии на фото можно открыть его в полном размере</i>

#ITновости #Технологии #Разработка"""
        
        return formatted_text

    def get_news_image(self, news_item):
        """Возвращает изображение для новости"""
        if news_item.get('image'):
            image_url = news_item['image']
            if image_url and image_url.startswith(('http://', 'https://')):
                return image_url
        return None