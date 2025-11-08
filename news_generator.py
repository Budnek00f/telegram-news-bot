import os
import requests
import logging
import random
import json
import time
import re

logger = logging.getLogger(__name__)

class NewsGenerator:
    def __init__(self):
        try:
            self.yandex_api_key = os.getenv('YANDEX_API_KEY')
            self.yandex_folder_id = os.getenv('YANDEX_FOLDER_ID')
            
            if not self.yandex_api_key:
                raise ValueError("YANDEX_API_KEY не установлен")
            if not self.yandex_folder_id:
                raise ValueError("YANDEX_FOLDER_ID не установлен")
            
            self.news_topics = [
                "искусственный интеллект и машинное обучение",
                "кибербезопасность и защита данных", 
                "облачные технологии и DevOps",
                "мобильная разработка и приложения",
                "веб-разработка и фронтенд технологии",
                "блокчейн и криптовалюты",
                "интернет вещей (IoT)",
                "игровая индустрия и геймдев",
                "аналитика данных и Big Data",
                "программирование и языки разработки"
            ]
            
            logger.info("✅ NewsGenerator инициализирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации NewsGenerator: {e}")
            raise

    def generate_news_with_yandex_gpt(self, topic):
        """Генерирует новость с помощью Yandex GPT"""
        try:
            logger.info(f"🧠 Генерация новости на тему: {topic}")
            
            headers = {
                "Authorization": f"Api-Key {self.yandex_api_key}",
                "Content-Type": "application/json",
                "x-folder-id": self.yandex_folder_id
            }
            
            prompt = f'''
            Напиши короткую IT-новость на тему "{topic}".
            Используй ТОЛЬКО следующие HTML теги: <b>, </b>, <i>, </i>
            НЕ используй: <!doctype>, <html>, <head>, <body>, <p>, <br>
            Длина: 200-400 символов.
            Формат:
            <b>Заголовок</b>
            Текст новости...
            <i>Список:</i>
            • Пункт 1
            • Пункт 2
            '''
            
            data = {
                "modelUri": f"gpt://{self.yandex_folder_id}/yandexgpt/latest",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.7,
                    "maxTokens": 1000
                },
                "messages": [
                    {
                        "role": "user",
                        "text": prompt
                    }
                ]
            }
            
            logger.info("📡 Отправка запроса к Yandex GPT...")
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                news_text = result['result']['alternatives'][0]['message']['text']
                formatted_text = self._clean_html(news_text)
                logger.info(f"✅ Новость сгенерирована, длина: {len(formatted_text)} символов")
                return formatted_text
            else:
                logger.error(f"❌ Ошибка Yandex GPT: {response.status_code} - {response.text}")
                return self._generate_fallback_news(topic)
                
        except Exception as e:
            logger.error(f"❌ Ошибка при генерации новости: {e}")
            return self._generate_fallback_news(topic)

    def _clean_html(self, text):
        """Очищает HTML от неподдерживаемых тегов"""
        # Удаляем <!doctype>, <html>, <head>, <body>
        text = re.sub(r'<!DOCTYPE[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<html[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</html>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<head[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</head>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<body[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</body>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<p[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
        
        # Убираем лишние символы
        text = text.replace('```html', '').replace('```', '').strip()
        
        # Добавляем хештеги
        if '#' not in text:
            text += "\n\n#ITновости #Технологии #Разработка"
            
        return text

    def _generate_fallback_news(self, topic):
        """Резервная новость если Yandex GPT недоступен"""
        logger.info(f"🔄 Использование резервной новости для темы: {topic}")
        
        fallback_news = f"""<b>🚀 Новости в сфере {topic}</b>

Крупные компании представили инновационные решения в области {topic}. Новые технологии обещают улучшить производительность и безопасность.

<i>Основные преимущества:</i>
• Увеличение скорости обработки данных
• Улучшение систем безопасности
• Снижение операционных затрат

#ITновости #Технологии #Разработка"""
        return fallback_news

    def get_random_topic(self):
        """Возвращает случайную тему"""
        topic = random.choice(self.news_topics)
        logger.info(f"🎲 Выбрана тема: {topic}")
        return topic

    def generate_complete_news(self):
        """Генерирует полную новость (без изображений)"""
        logger.info("�� Начало генерации новости")
        topic = self.get_random_topic()
        news_text = self.generate_news_with_yandex_gpt(topic)
        
        logger.info("✅ Новость сгенерирована")
        return news_text, None
