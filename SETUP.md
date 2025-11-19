# Setup Instructions

## Первоначальная настройка проекта

### 1. Клонирование репозитория
```bash
git clone https://github.com/xumezzan/marketplace-project.git
cd marketplace-project/services-marketplace
```

### 2. Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

**ВАЖНО:** Сгенерируйте новый SECRET_KEY:
```bash
python -c 'from django.core.management.utils importget_random_secret_key; print(get_random_secret_key())'
```

Вставьте полученный ключ в `.env`:
```
DJANGO_SECRET_KEY=ваш-сгенерированный-ключ-здесь
```

###5. Применение миграций
```bash
cd backend
python manage.py migrate
```

### 6. Создание суперпользователя
```bash
python manage.py createsuperuser
```

### 7. Сбор статических файлов
```bash
python manage.py collectstatic --no-input
```

### 8. Запуск сервера разработки
```bash
python manage.py runserver
```

Откройте http://localhost:8000 в браузере.

---

## Production Development

### Render.com

1. Создайте новый Web Service на Render
2. Подключите GitHub репозиторий
3. Настройте Environment Variables:
   - `DJANGO_SECRET_KEY` - сгенерируйте новый ключ
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=your-app.onrender.com`
   - `DATABASE_URL` - Render предоставит автоматически
   - `RENDER_EXTERNAL_HOSTNAME=your-app.onrender.com`
   - `USE_TLS=True`
   - `IS_BEHIND_PROXY=True`

4. Build Command: `pip install -r requirements.txt && python backend/manage.py collectstatic --no-input && python backend/manage.py migrate`
5. Start Command: `cd backend && gunicorn config.wsgi:application`

---

## Темная тема

Темная тема реализована с использованием Tailwind CSS `darkMode: 'class'` и CSS переменных.

### Использование
- Переключатель находится в правом верхнем углу navbar (иконка луны/солнца)
- Выбор сохраняется в localStorage
- Автоматически учитывается системное предпочтение пользователя

### Цветовая палитра Midnight
- Фон (темный): Slate 950 (#020617)
- Карточки: Slate 900 (#0f172a)
- Текст: Slate 50 (#f8fafc)
- Границы: Slate 800 (#1e293b)

---

## Безопасность

### ✅ Реализовано
- HTTPS redirect (за прокси)
- Secure cookies
- HSTS headers
- XSS protection
- Content-type sniffing protection
- Clickjacking protection
- CSRF protection

### ⚠️ Важно
- **НИКОГДА** не коммитьте `.env` в репозиторий
- Генерируйте уникальный SECRET_KEY для каждого окружения
- В production **ОБЯЗАТЕЛЬНО** укажите конкретные домены в ALLOWED_HOSTS

---

## Troubleshooting

### ERROR: DJANGO_SECRET_KEY environment variable is not set
**Решение:** Создайте `.env` файл и укажите SECRET_KEY (см. шаг 4)

### ERROR: DJANGO_ALLOWED_HOSTS must be set in production
**Решение:** Добавьте DJANGO_ALLOWED_HOSTS в environment variables

### Темная тема не работает
**Решение:** Очистите кэш браузера и localStorage

### Статические файлы не загружаются
**Решение:** Выполните `python manage.py collectstatic --no-input`

---

## Дополнительная информация

- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Render Deployment Guide](https://render.com/docs/deploy-django)
