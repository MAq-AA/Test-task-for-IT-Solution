# Django Quotes Project

## Фишки проекта

- **Умный выбор цитат** - взвешенный случайный выбор с учетом веса цитат
- **Кастомная аутентификация** - свои формы входа/регистрации с редиректом назад
- **Адаптивный дизайн** - работает на всех устройствах
- **Быстрые редиректы** - после входа возвращает на предыдущую страницу
- **SQLite база** - не требует дополнительной настройки
- **Чистые шаблоны** - минималистичный дизайн

## 🚀 Быстрый запуск

```
# 1. Клонировать и перейти в папку
git clone https://github.com/MAq-AA/Test-task-for-IT-Solution.git
cd Test-task-for-IT-Solution

# 2. Активировать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Применить миграции
python manage.py migrate

# 5. Запустить сервер
python manage.py runserver
```
Перейдите по ссылке: http://127.0.0.1:8000
