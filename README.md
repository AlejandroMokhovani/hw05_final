# Yatube
***
### Описание:
Проект для ведения своего и просмотра блогов других пользователей.

Пользователь может:
- Регистрироваться
- Создавать, редактировать и комментировать посты. Редактировать можно только свои посты
- Просматривать посты по группам, подписываться на других пользователей и просматривать посты этих пользователей в отдельной ленте. Группы для постов может создавать только администратор

Большая часть проекта покрыта тестами.
### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:AlejandroMokhovani/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

Так как при развертывании проекте локально база данных будет пустой, то на главной стрнице не будет никаких постов. Чтобы посмотреть как они выглядят нужно зарегистрироваться и создать пост. Создайте еще нескольких пользователей, если хотите посмотреть весь функционал (подписка, лента новостей).

### Технологии:
- [Django](https://github.com/django/django) - фреймворк для создания бекэнда сайта
- [Bootstrap](https://github.com/twbs/bootstrap) - некоторая часть фронтэнда
