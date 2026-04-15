# LigaPay

LigaPay — портфолио-проект, представляющий собой маркетплейс по игре League of Legends.

Пользователи могут регистрироваться, просматривать игровые товары и услуги, оформлять заказы, управлять внутренним кошельком и общаться в чатах.
Проект сфокусирован на backend-разработке и демонстрирует работу с асинхронными задачами, WebSocket и контейнеризацией.

## Содержание

- [Основной функционал](#основной-функционал)
- [Стек технологий](#стек-технологий)
- [Запуск проекта локально (dev)](#запуск-проекта-локально-dev)
- [Запуск проекта через Docker (prod-like)](#запуск-проекта-через-docker-prod-like)
- [Тестирование](#тестирование)
- [Deployment проекта на удаленный сервер](#Deployment-проекта-на-удаленный-сервер)

## Основной функционал

- Регистрация и авторизация пользователей
- Покупка товаров и услуг:
  - у других пользователей (маркетплейс)
  - напрямую у сайта
- Продажа товаров другим пользователям
- Внутренний кошелёк:
  - пополнение баланса
  - заморозка средств
  - списание средств при покупке
- Подтверждение или отклонение сделок
- Система чатов:
  - глобальный чат
  - личный чат между покупателем и продавцом

## Стек технологий

**Backend:**
- Python 3.12
- Django 5
- Django Channels (WebSocket)
- Celery
- Redis
- PostgreSQL

**Тестирование:**
- unittest (Django TestCase)
- Асинхронные тесты WebSocket
- Selenium (browser-тесты)

**Инфраструктура:**
- Docker / Docker Compose
- Daphne (ASGI)
- Flower (мониторинг Celery)
- WhiteNoise (static files)


## Запуск проекта локально (dev)

**1. Клонируйте репозиторий и перейдите в папку проекта**
```bash
git clone https://github.com/CrazyBabyBoy01/LigaPay.git
```

**2. Зайдите в рабочую директорию проекта**
```bash
cd LigaPay
```

**3. Создайте виртуальное окружение**

```bash
python -m venv venv
```
**4. Активируйте виртуальное окружение**

- Windows

```bash
venv\Scripts\activate
```

- Linux / macOS

```bash
source venv/bin/activate
```

**5. Обновите pip**

```bash
python -m pip install --upgrade pip
```

**6. Установите зависимости**

```bash
pip install -r requirements.txt
```

**7. Создайте файл .env в корне проекта и заполните переменные окружения**

```bash
SECRET_KEY=your_secret_key
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

EMAIL_HOST=your_email_host
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password

REDIS_HOST=localhost
REDIS_PORT=6379
```

**8. Примените миграции**

```bash
python manage.py migrate
```

**9. Запустите сервер разработки**

```bash
python manage.py runserver
```

**Проект будет доступен по адресу:**
```bash
http://127.0.0.1:8000/
```

## Запуск проекта через Docker (prod-like)

**1. Убедитесь, что Docker и Docker Compose установлены**

**2. Склонируйте репозиторий и перейдите в папку проекта**
```bash
git clone https://github.com/CrazyBabyBoy01/LigaPay.git
```

**3. Зайдите в рабочую директорию проекта**
```bash
cd LigaPay
```

**4. Создайте файл .env в корне проекта и заполните переменные окружения**

```bash
SECRET_KEY=your_secret_key
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

EMAIL_HOST=your_email_host
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password

REDIS_HOST=localhost
REDIS_PORT=6379
```

**5. Запустите Docker Desktop**

**6. Соберите и запустите контейнеры**

```bash
docker-compose up --build
```

**7. Выполните миграции внутри контейнера**

```bash
docker exec -it web python manage.py migrate
```

**8. Соберите статические файлы**

```bash
docker exec -it web python manage.py collectstatic --noinput
```

**Проект будет доступен по адресу:**

```bash
http://localhost:8000/
```

## Тестирование

В проекте реализовано модульное и интеграционное тестирование.

Используется стандартный `unittest` (Django TestCase), а также асинхронные тесты для WebSocket и browser-тесты.

Тесты запускаются в отдельном тестовом окружении и не требуют Redis.

Для этого используется файл `manage_test.py`, который подключает
настройки `LigaPay.settings.test`.

```bash
python manage_test.py test
```

**Особенности тестирования:**

- Redis не требуется
- Celery работает в синхронном режиме (eager)
- WebSocket тестируется с использованием InMemoryChannelLayer
- Покрыта бизнес-логика, формы и WebSocket-чаты
- Реализованы browser-тесты с использованием Selenium

# Deployment проекта на удаленный сервер

**1. Войдите на удаленный сервер с помощью SSH или FTP**

linux/macOS

```bash
ssh username@server_ip
```

далее введите пароль для подключения.
Windows

Для подключения по SSH на Windows можно использовать следующее ПО, Putty или MobaXterm

**2. Установите Docker**

```bash
apt update
apt install -y docker.io docker-compose
```

Проверьте:

```bash
docker --version
docker-compose --version
```

**3. Загрузите файлы проекта на удаленный сервер**

```bash
git clone https://github.com/CrazyBabyBoy01/LigaPay.git
cd LigaPay
```

**4. Создайте файл .env и заполните его по примеру**


```bash
nano .env
SECRET_KEY=
DJANGO_SETTINGS_MODULE=LigaPay.settings.prod
ALLOWED_HOSTS=

# Postgres
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# Email
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

**5. Запустите проект**

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

**6. Проверьте**

```bash
docker exec -it web printenv | grep POSTGRES
```

нужно увидеть:

```bash
POSTGRES_HOST=postgres
```

Потом сразу, проверяем сайт:


```bash
http://ВАШ_IP:8000
```

**7. Настройте домен**

В корне проекта, есть папка nginx.
В папке нам необходимо открыть nginx.conf и отредактировать пару строчек.

```bash
server_name ваш домен;
```

Так же необходимо отредактировать .env.

```bash
ALLOWED_HOSTS= домен, IP,127.0.0.1,localhost;
```
